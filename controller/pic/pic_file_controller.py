

from flask import Blueprint, abort, send_from_directory
import os
from models.pic.pic import Pic
from manager.db_manager import get_session
from utils.basic.logging_utils import get_logger
from utils.file_utils import get_images_dir, get_app_dir

pic_file_bp = Blueprint('i', __name__)

logger = get_logger(__name__)

# 获取图片 url
@pic_file_bp.route("/i/<filename>")
def serve_file(filename):
    # filename 形式: <uuid>.jpg
    file_uuid, suffix = os.path.splitext(filename)
    with get_session() as db:
        pic = db.query(Pic).filter(Pic.uuid == file_uuid).first()
        if not pic:
            abort(404)

        # 确认路径
        image_folder = get_images_dir()
        target_folder = os.path.join(image_folder, pic.relative_path)
        full_path = os.path.join(str(target_folder), pic.uuid + pic.pic_suffix)

        if not os.path.exists(full_path):
            abort(404)

        logger.info(f"获取 {filename} 图片")
        return send_from_directory(str(target_folder), pic.uuid + pic.pic_suffix)

# 获取图片路由
@pic_file_bp.route('/web/<filename>')
def get_web_file(filename):
    app_folder = get_app_dir()
    target_folder = os.path.join(app_folder, 'web-conf')
    logger.info(f"获取 {filename} 路由")
    return send_from_directory(target_folder, filename)

# 获取缩略图 url
@pic_file_bp.route("/thumbnail/<filename>")
def serve_thumbnail(filename):
    # filename 形式: <uuid>.jpg
    file_uuid, suffix = os.path.splitext(filename)
    with get_session() as db:
        pic = db.query(Pic).filter(Pic.uuid == file_uuid).first()
        if not pic:
            abort(404)

        # 确认路径
        images_folder = get_images_dir()
        target_folder = os.path.join(images_folder, 'thumbnail')
        full_path = os.path.join(str(target_folder), pic.uuid + pic.pic_suffix)

        if not os.path.exists(full_path):
            abort(404)

        logger.info(f"获取 {filename} 缩略图")
        return send_from_directory(str(target_folder), pic.uuid + pic.pic_suffix)
