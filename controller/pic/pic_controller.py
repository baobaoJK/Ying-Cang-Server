# 图片控制器

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from decorators.browser_decorators import browser_only
from services.pic.pic_service import PicService
from utils import ResponseFactory
from utils.basic.logging_utils import get_logger

pic_bp = Blueprint('pic', __name__, url_prefix='/api')

pic_service = PicService()

logger = get_logger(__name__)

# 获取图片数量
@pic_bp.route("/getPicCount", methods=['GET'])
@browser_only
def get_pic_count():
    return pic_service.get_pic_count().to_response()

# 获取图片列表
@pic_bp.route("/getPicList", methods=['GET'])
@jwt_required()
@browser_only
def get_pic_list():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("perPage", default=30, type=int)
    album_id = request.args.get("albumId", default=1, type=int)
    order = request.args.get("order", default="newest", type=str)
    keyword = request.args.get("keyword", default="", type=str)

    # 获取响应标头
    logger.warning(f"前端传过来的指是 {page} - {per_page} - {album_id}")
    return pic_service.get_pic_list(page, per_page, album_id, order, keyword).to_response()

# 修改图片信息
@pic_bp.route('/pic', methods=['PUT'])
@jwt_required()
@browser_only
def update_pic():
    pid = request.json.get('pid')
    value = request.json.get('value', None)

    if not pid or not value:
        logger.error("图片名称不能为空")
        return ResponseFactory.success(data={
            'message': 'pic.message.picNameEmpty',
            'messageType': 'error'
        }).to_response()

    logger.info(f"修改图片信息: {pid} {value}")
    return pic_service.update_pic(pid, value).to_response()

# 删除图片
@pic_bp.route('/pic', methods=['DELETE'])
@jwt_required()
def delete_pic():
    delete_pic_list = request.json.get('deletePicList')

    if not delete_pic_list or len(delete_pic_list) == 0:
        logger.error("图片不能为空")
        return ResponseFactory.success(data={
            'message': 'pic.message.picEmpty',
            'messageType': 'error'
        }).to_response()

    logger.info(f"删除图片列表: {delete_pic_list}")
    return pic_service.delete_pic(delete_pic_list).to_response()

# 移动图片
@pic_bp.route('/pic', methods=['POST'])
@jwt_required()
def move_pic():
    move_pic_list = request.json.get('movePicList')
    album_id = request.json.get('albumId', None)

    if not move_pic_list or len(move_pic_list) == 0  or album_id is None:
        logger.error("图片或相册不能为空")
        return ResponseFactory.success(data={
            'message': 'pic.message.picOrAlbumEmpty',
            'messageType': 'error'
        }).to_response()

    logger.error(f"移动图片列表: {move_pic_list} - 相册ID: {album_id}")
    return pic_service.move_pic(move_pic_list, album_id).to_response()