# 图片文件夹控制类

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from services.pic.album_service import AlbumService
from utils import ResponseFactory
from utils.basic.logging_utils import get_logger

album_bp = Blueprint('album', __name__, url_prefix='/api')

album_service = AlbumService()

logger = get_logger(__name__)

# 获取相册列表
@album_bp.route('/album', methods=['GET'])
@jwt_required()
def get_pic_folder_list():
    logger.info("获取相册列表")
    return album_service.get_album_list().to_response()

# 创建相册
@album_bp.route('/album', methods=['POST'])
@jwt_required()
def create_pic_folder():
    album_name = request.json.get('albumName')

    if not album_name:
        logger.error("相册名称不能为空")
        return ResponseFactory.success(data={
            'message': 'album.message.albumNameIsNone',
            'messageType': 'error'
        }).to_response()

    logger.info(f"创建名称为 {album_name} 的相册")
    return album_service.create_album(album_name).to_response()

# 修改相册名称
@album_bp.route('/album', methods=['PUT'])
@jwt_required()
def update_pic_folder():
    rename = request.json.get('rename')
    aid = request.json.get('aid')

    if not rename or not aid:
        logger.error("相册名称不能为空")
        return ResponseFactory.success(data={
            'message': 'album.message.albumNameIsNone',
            'messageType': 'error'
        }).to_response()

    logger.info(f"修改 aid 为 {aid} 的相册新名称 {rename}")
    return album_service.update_album_name(aid, rename).to_response()

# 删除相册
@album_bp.route('/album', methods=['DELETE'])
@jwt_required()
def delete_pic_folder():
    aid = request.json.get('aid')

    if not aid or aid == 1:
        logger.error("相册id不能为空")
        return ResponseFactory.success(data={
            'message': 'album.message.albumIdIsNull',
            'messageType': 'error'
        }).to_response()

    logger.info(f"删除 aid 为 {aid} 的相册")
    return album_service.delete_album(aid).to_response()