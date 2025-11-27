import os.path
from datetime import datetime

from sqlalchemy import func

from manager.db_manager import get_session
from models.pic.pic import Pic
from models.pic.album import Album
from utils import ResponseFactory
from utils.basic.logging_utils import get_logger
from utils.file_utils import get_images_dir

logger = get_logger(__name__)

# 相册服务类
class AlbumService:

    """
        创建相册
    """
    @staticmethod
    def create_album(album_name: str):
        with get_session() as db:
            try:
                # 判断相册是否存在
                sql_album = db.query(Album).filter(Album.album_name == album_name).first()
                if sql_album is not None:
                    logger.error("相册已存在")
                    return ResponseFactory.success(data={
                        'message': 'album.message.albumAlreadyExists',
                        'messageType': 'error'})

                album = Album()
                album.album_name = album_name
                album.create_time = datetime.now()
                db.add(album)
                db.commit()
                logger.info("相册创建成功")
                return ResponseFactory.success(data={
                    'message': 'album.message.albumCreatedSuccessfully',
                    'messageType': 'success'
                })
            except Exception as e:
                db.rollback()
                logger.error(f"创建相册失败: {e}")
                return ResponseFactory.success(data={
                    'message': e,
                    'messageType': 'error'
                })

    """
        获取相册列表
    """
    @staticmethod
    def get_album_list():
        with get_session() as db:
            try:
                album_list = (
                    db.query(
                        Album.aid,
                        Album.album_name,
                        func.count(Pic.pid).label('pic_count')  # 用 aid 统计，不会误差
                    )
                    .outerjoin(Pic, Pic.album_id == Album.aid)
                    .group_by(Album.aid, Album.album_name) # 按照 pic_folder_name 分组
                    .order_by(Album.aid)
                    .all()
                )

                # 在 album_list 前插入 我的最爱 相册
                my_love_album_aid = 0
                my_love_album_name = 'love'
                my_love_album_count = db.query(Pic).filter(Pic.pic_love == 1).count()

                album_list.insert(1, (my_love_album_aid, my_love_album_name, my_love_album_count))

                logger.info(f"获取相册列表成功：{[folder for folder in album_list]}")
                return ResponseFactory.success(data={
                    'albumList': [{'aid': folder[0], 'albumName': folder[1], 'picCount': folder[2]} for folder in album_list]
                })
            except Exception as e:
                logger.error(f"获取相册列表失败: {e}")
                return ResponseFactory.success(data={
                    'message': e,
                    'messageType': 'error'})

    """
        修改相册名称
    """
    @staticmethod
    def update_album_name(aid: int, rename: str):

        with get_session() as db:
            try:
                sql_album_id = db.query(Album).filter(Album.aid == aid).first()
                if sql_album_id is None:
                    logger.error(f"aid 为 {aid} 的相册不存在")
                    return ResponseFactory.success(data={
                        'message': 'album.message.albumDoesNotExist',
                        'messageType': 'error'
                    })

                sql_album = db.query(Album).filter(Album.album_name == rename).first()
                if sql_album is not None:
                    logger.error("相册已存在")
                    return ResponseFactory.success(data={
                        'message': 'album.message.albumAlreadyExists',
                        'messageType': 'error'})

                # 修改相册名称
                album = db.query(Album).filter(Album.aid == aid).first()
                album.album_name = rename
                db.commit()

                logger.info("相册名称修改成功")
                return ResponseFactory.success(data={
                    'message': 'album.message.albumNameModifiedSuccessfully',
                    'messageType': 'success'
                })
            except Exception as e:
                db.rollback()
                logger.error(f"修改相册失败: {e}")
                return ResponseFactory.success(data={
                    'message': e,
                    'messageType': 'error'
                })

    # 删除相册
    @staticmethod
    def delete_album(aid: int):
        with get_session() as db:
            try:
                # 获取相册信息
                album = db.query(Album).filter(Album.aid == aid).first()
                if album is not None:
                    # 删除数据库数据
                    db.delete(album)
                    pic_list = db.query(Pic).filter(Pic.album_id == album.aid).all()
                    if pic_list is not None:
                        for pic in pic_list:
                            db.delete(pic)

                            pic_folder = os.path.join(str(get_images_dir()), pic.relative_path)
                            pic_file = os.path.join(pic_folder, pic.uuid + pic.pic_suffix)
                            if os.path.exists(pic_file):
                                os.remove(pic_file)

                    db.commit()

                logger.info("相册删除成功")
                return ResponseFactory.success(data={
                    'message': 'album.message.albumIsDeleted',
                    'messageType': 'success'})

            except Exception as e:
                db.rollback()
                logger.error(f"删除相册失败: {e}")
                return ResponseFactory.success(data={
                    'message': e,
                    'messageType': 'error'})
