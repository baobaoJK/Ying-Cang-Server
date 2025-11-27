from flask import Blueprint, request

from api.decorators.api_required import token_required
from services.pic.album_service import AlbumService
from utils import ResponseFactory
from utils.basic.logging_utils import get_logger

api_album_bp = Blueprint('api_album', __name__, url_prefix='/api/x')

album_service = AlbumService()

logger = get_logger(__name__)


# 获取相册列表
@api_album_bp.route('/album', methods=['GET'])
@token_required
def get_albums():
    return album_service.get_album_list().to_response()

# 创建相册
@api_album_bp.route('/album', methods=['POST'])
@token_required
def create_album():
    album_name = request.json.get('albumName')

    if not album_name:
        logger.error('相册名称不能为空')
        return ResponseFactory.error(data=False).to_response()

    result = album_service.create_album(album_name)

    if result.data.get('messageType') == 'success':
        return ResponseFactory.success(data=True).to_response()
    else:
        return ResponseFactory.error(data=False).to_response()

# 删除相册
@api_album_bp.route('/album', methods=['DELETE'])
@token_required
def delete_album():
    album_id = request.json.get('albumId')

    if not album_id or album_id == 1:
        logger.error('相册id不能为空')
        return ResponseFactory.error(data=False).to_response()

    result = album_service.delete_album(album_id)

    if result.data.get('messageType') == 'success':
        return ResponseFactory.success(data=True).to_response()
    else:
        return ResponseFactory.error(data=False).to_response()