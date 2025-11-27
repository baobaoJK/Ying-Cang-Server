# 上传图片控制器

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from decorators.browser_decorators import browser_only
from services.pic.upload_service import UploadService
from utils.basic.logging_utils import get_logger
from utils.file_utils import check_file

upload_bp = Blueprint('/upload', __name__, url_prefix='/api')

upload_service = UploadService()

logger = get_logger(__name__)

# 图片上传
@upload_bp.route('/upload', methods=['POST'])
@jwt_required()
@browser_only
def upload():
    # 检查文件是否符合类型
    file_stage = check_file(request.files)
    if file_stage is not None:
        return file_stage

    file = request.files["file"]

    # 获取用户选择的子目录
    album_id = request.form.get("albumId", "").strip()
    logger.info(f"上传图片至-相册 ID 为 {album_id} 的相册")
    result = upload_service.handle_upload(file, int(album_id))

    return result.to_response()