import json
import threading

import globals as g
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from decorators.browser_decorators import browser_only
from services.setting_service import SettingService
from utils import ResponseFactory
from utils.basic.logging_utils import get_logger
from utils.sql_utils import download_sql, import_sql
from utils.zip_utils import download_zip, generate_zip, unzip

logger = get_logger(__name__)

# 设置页面路由
setting_bp = Blueprint('setting', __name__, url_prefix='/api')

# 设置服务类
setting_service = SettingService()

# 获取网页设置信息
@setting_bp.route('/getWebSetting', methods=['GET'])
def get_web_setting():
    result = setting_service.get_web_setting()
    logger.info("获取网页设置信息")
    return result.to_response()

# 更新网页设置信息
@setting_bp.route('/updateWebSetting', methods=['PUT'])
@jwt_required()
def update_web_setting():
    web_setting_form = request.form
    web_site = web_setting_form.get('site')
    web_site = json.loads(web_site)

    #  更换网页 Logo
    web_logo = request.files.get('webLogo', None)

    # 更换网页 SVG Logo
    web_svg_logo = request.files.get('webSVGLogo', None)

    # 更换网页登录封面
    web_login_bg = request.files.get('loginCover', None)

    # 更换网页背景图片
    web_background = request.files.get('background', None)

    result = setting_service.update_web_setting(web_site, web_logo, web_svg_logo, web_login_bg, web_background)
    logger.info("更新网页设置信息")
    return result.to_response()

# 获取用户设置信息
@setting_bp.route('/getUserSetting', methods=['GET'])
@jwt_required()
def get_user_setting():
    result = setting_service.get_user_setting()
    logger.info("获取用户设置信息")
    return result.to_response()

# 更新用户设置信息
@setting_bp.route('/updateUserSetting', methods=['POST'])
@jwt_required()
def update_user_setting():
    # 用户信息
    user_setting_form = request.form
    user_form = user_setting_form.get('form')
    user_form = json.loads(user_form)
    user_name = user_form.get('username', None)
    pass_word = user_form.get('password', None)

    # 用户头像
    avatar_img = request.files.get('avatar', None)

    result = setting_service.update_user_setting(avatar_img, user_name, pass_word)
    logger.info("更新用户设置信息")
    return result.to_response()


# 压缩图片文件
@setting_bp.route("/export_progress", methods=['GET'])
@jwt_required()
@browser_only
def export_progress():
    threading.Thread(target=generate_zip).start()
    logger.info("开始压缩图片")
    return ResponseFactory.success(data={
        "message": "ok",
        "messageType": "success"
    }).to_response()

# 获取进度
@setting_bp.route("/export_progress_status", methods=['GET'])
@jwt_required()
def export_progress_status():
    """返回当前进度"""
    return ResponseFactory.success(data={
        "progress": g.zip_progress
    }).to_response()

# 下载图片
@setting_bp.route('/downloadImages', methods=['GET'])
@jwt_required()
@browser_only
def download_images():
    logger.info("下载图片")
    return download_zip()

# 下载 SQL 文件
@setting_bp.route("/downloadSql", methods=['GET'])
@jwt_required()
@browser_only
def export_db():
    logger.info("下载 SQL 文件")
    return download_sql()

# 导入图片
@setting_bp.route('/importImages', methods=['POST'])
@jwt_required()
@browser_only
def import_images():
    """导入图片 ZIP"""
    if "file" not in request.files:
        return ResponseFactory.error(data={
            "message": "setting.fileManager.message.fileIsEmpty",
            "messageType": "error"
        }).to_response()

    file = request.files["file"]
    if file.filename == "":
        return ResponseFactory.error(data={
            "message": "setting.fileManager.message.fileNameIsEmpty",
            "messageType": "error"
        }).to_response()

    logger.info(f"导入图片 ZIP: {file.filename}")
    return unzip(file)

@setting_bp.route("/importSql", methods=["POST"])
@jwt_required()
@browser_only
def import_db_sql():
    """导入 SQL 文件到 MySQL/PostgreSQL"""
    if "file" not in request.files:
        return ResponseFactory.error(data={
            "message": "setting.fileManager.message.fileIsEmpty",
            "messageType": "error"
        }).to_response()

    file = request.files["file"]

    logger.info(f"导入 SQL 文件: {file.filename}")
    return import_sql(file)