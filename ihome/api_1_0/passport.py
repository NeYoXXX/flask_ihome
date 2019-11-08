from sqlalchemy.exc import IntegrityError

from ihome import redis_store, db
from ihome.models import User
from ihome.utils.response_code import RET, error_map
from . import api
from flask import request, jsonify, current_app, session
import re


@api.route("/user", method=["POST"])
def register():
    par_dic = request.get_json()
    mobile = par_dic.get("mobile")
    image_code = par_dic.get("image_code")
    password = par_dic.get("password")
    password2 = par_dic.get("password2")

    if all([mobile, image_code, password, password2]):
        return jsonify(error=RET.PARAMERR, errmsg=error_map.get(RET.PARAMERR))
        # 判断手机号格式
    if not re.match(r"1[34578]\d{9}", mobile):
        # 表示格式不对
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg="两次密码不一致")
    '''
    # 从redis中取出短信验证码
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="读取真实短信验证码异常")

    # 判断短信验证码是否过期
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码失效")

    # 删除redis中的短信验证码，防止重复使用校验
    try:
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 判断用户填写短信验证码的正确性
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")
    '''
    try:
        is_image = redis_store.get("image_code_%s" % image_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取图片验证码时异常")
    if is_image is None:
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码已过期")

    try:
        redis_store.delete("image_code_%s" % image_code)
    except Exception as e:
        current_app.logger.error(e)


    if is_image != image_code:
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")

    #验证完成后添加数据
    user = User(name=mobile, mobile=mobile)
    # user.generate_password_hash(password)

    user.password = password  # 设置属性

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 数据库操作错误后的回滚
        db.session.rollback()
        # 表示手机号出现了重复值，即手机号已注册过
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")
    except Exception as e:
        db.session.rollback()
        # 表示手机号出现了重复值，即手机号已注册过
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库异常")

    # 保存登录状态到session中
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id

    # 返回结果
    return jsonify(errno=RET.OK, errmsg="注册成功")
