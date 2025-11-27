from flask import Blueprint, request

from api.decorators.api_required import token_required
from services.pic.pic_service import PicService
from services.pic.upload_service import UploadService
from utils import ResponseFactory
from utils.basic.logging_utils import get_logger
from utils.file_utils import check_file

api_upload_bp = Blueprint('api_upload', __name__, url_prefix='/api/x')

upload_service = UploadService()

pic_service = PicService()

logger = get_logger(__name__)

# 图片上传
@api_upload_bp.route('/upload', methods=['POST'])
@token_required
def upload():

    # 检查文件是否符合类型
    file_stage = check_file(request.files)
    if file_stage is not None:
        logger.error('文件类型不符合要求')
        return ResponseFactory.error(data=False).to_response()

    file = request.files["file"]

    # 获取相册 ID
    album_id = request.form.get("albumId", "").strip()
    result = upload_service.handle_upload(file, int(album_id))

    if result.data.get('filename', None) is not None:
        return result.to_response()
    else:
        return ResponseFactory.error(data=False).to_response()

# 获取图片列表
@api_upload_bp.route('/getPicList', methods=['GET'])
@token_required
def get_pic_list():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("perPage", default=30, type=int)
    album_id = request.args.get("albumId", default=1, type=int)
    order = request.args.get("order", default="newest", type=str)
    keyword = request.args.get("keyword", default="", type=str)

    return pic_service.get_pic_list(page, per_page, album_id, order, keyword).to_response()


# 删除图片
@api_upload_bp.route('/pic', methods=['DELETE'])
@token_required
def delete_pic():
    delete_pic_list = request.json.get('deletePicList', None)

    if delete_pic_list is None or len(delete_pic_list) == 0:
        logger.error("图片不能为空")
        return ResponseFactory.error(data=False).to_response()

    result = pic_service.delete_pic(delete_pic_list)

    if result.data.get('messageType') == 'success':
        return ResponseFactory.success(data=True).to_response()
    else:
        return ResponseFactory.error(data=False).to_response()