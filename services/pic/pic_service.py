import os

from flask import url_for

from manager.db_manager import get_session
from models.pic.pic import Pic
from models.pic.album import Album
from utils import ResponseFactory
from utils.basic.logging_utils import get_logger
from utils.file_utils import get_images_dir, get_app_dir

logger = get_logger(__name__)

# 图片服务类
class PicService:
    """
        获取图片数量
    """
    @staticmethod
    def get_pic_count():
        with get_session() as db:
            try:
                pic_count = db.query(Pic).count()
                logger.info("获取图片数量成功")
                return ResponseFactory.success(data={
                    'picCount': pic_count
                })
            except Exception as e:
                logger.error("获取图片数量失败")
                return ResponseFactory.success(data={
                    'message': e
                })

    """
        获取图片列表
        支持分页和相册筛选
    """
    @staticmethod
    def get_pic_list(page: int, per_page: int, album_id: int, order: str, keyword: str):
        # 查询数据表
        with get_session() as db:
            try:
                if album_id != 0:
                    path = db.query(Album).filter(Album.aid == album_id).first()
                    if path is None:
                        logger.error("相册不存在")
                        return ResponseFactory.success(data={
                            'message': 'pic.message.albumIsNone',
                            'messageType': 'error'
                        })

                    path_pid = path.aid
                    total = db.query(Pic).filter(Pic.album_id == path_pid).count()
                else:
                    total = db.query(Pic).filter(Pic.pic_love == 1).count()

                order_mapping = {
                    'newest': Pic.upload_time.desc(),
                    'earliest': Pic.upload_time.asc(),
                    'utmost': Pic.pic_file_size.desc(),  # 假设size字段表示图片大小
                    'least': Pic.pic_file_size.asc()
                }

                # 获取排序参数，默认为newest
                order_by = order_mapping.get(order, Pic.upload_time.desc())

                # 构建查询
                if album_id != 0:
                    query = db.query(Pic).filter(Pic.album_id == path_pid)
                else:
                    query = db.query(Pic).filter(Pic.pic_love == 1)

                # 添加关键字搜索
                if keyword:
                    query = query.filter(Pic.pic_desc.contains(keyword))

                # 执行查询
                images = query.order_by(order_by) \
                    .offset((page - 1) * per_page) \
                    .limit(per_page) \
                    .all()

                image_list = []
                for img in images:
                    album_name = db.query(Album).filter(Album.aid == img.album_id).first().album_name
                    # 使用 url_for 自动生成完整 URL
                    file_url = url_for("i.serve_file", filename=(img.uuid + img.pic_suffix))
                    thumbnail_url = url_for("i.serve_thumbnail", filename=(img.uuid + img.pic_suffix))
                    img_object = img.to_dict()
                    img_object['url'] = file_url
                    img_object['albumName'] = album_name
                    img_object['thumbnailUrl'] = thumbnail_url
                    image_list.append(img_object)

                logger.info("获取图片列表成功")
                return ResponseFactory.success(data={
                    "page": page,
                    "perPage": per_page,
                    "total": total,
                    "images": image_list
                })

            except Exception as e:
                logger.error(f"获取图片列表失败: {e}")
                return ResponseFactory.success(data={
                    'message': e,
                    'messageType': 'error'
                })

    """
        修改图片信息
    """
    @staticmethod
    def update_pic(pid: int, value: dict):
        with get_session() as db:
            try:
                pic = db.query(Pic).filter(Pic.pid == pid).first()
                if pic is not None:

                    # 更改描述
                    description = value.get("description", None)
                    if description is not None:
                        pic.pic_desc = description

                    # 更改名称
                    rename = value.get("rename", None)
                    if rename is not None:
                        pic.pic_name = rename

                    # 设为最爱
                    love = value.get("love", None)
                    if love is not None:
                        pic.pic_love = love

                    db.commit()
                    logger.info("修改图片信息成功")
                    return ResponseFactory.success(data={
                        'message': 'pic.message.picUpdateSuccess',
                        'messageType': 'success'
                    })
                else:
                    logger.error("图片不存在")
                    return ResponseFactory.success(data={
                        'message': 'pic.message.picIsNone',
                        'messageType': 'error'
                    })
            except Exception as e:
                db.rollback()
                logger.error(f"修改图片名称失败: {e}")
                return ResponseFactory.success(data={
                    'message': e,
                    'messageType': 'error'
                })

    """
        删除图片
    """
    @staticmethod
    def delete_pic(delete_pic_list: list):
        image_folder = get_images_dir()
        with get_session() as db:
            try:
                for pid in delete_pic_list:
                    img = db.query(Pic).filter(Pic.pid == pid).first()
                    if img is not None:
                        pic_folder = db.query(Album).filter(Album.aid == img.album_id).first()
                        logger.warning(f"文件夹名称{pic_folder.album_name}")

                        target_folder = os.path.join(image_folder, img.relative_path)

                        url = os.path.join(str(target_folder), str(img.uuid + img.pic_suffix))

                        if os.path.exists(url):
                            db.delete(img)
                            db.commit()
                            os.remove(url)
                            thumbnail_url = os.path.join(get_app_dir(), 'images/thumbnail', str(img.uuid + img.pic_suffix))
                            if os.path.exists(thumbnail_url):
                                os.remove(thumbnail_url)

                logger.info("删除图片成功")
                return ResponseFactory.success(data={
                    'message': 'pic.message.picDeleteSuccess',
                    'messageType': 'success'
                })

            except Exception as e:
                logger.error(f"删除图片失败: {e}")
                return ResponseFactory.success(data={
                    'message': e,
                    'messageType': 'error'
                })

    """
        移动图片
    """
    @staticmethod
    def move_pic(move_pic_list: list, path_pid: int):
        with get_session() as db:
            try:

                # 设为最爱
                if path_pid == 0:
                    for pid in move_pic_list:
                        pic = db.query(Pic).filter(Pic.pid == pid).first()
                        if pic is not None:
                            pic.pic_love = 1

                    db.commit()
                else:
                    # 移动到指定相册
                    album = db.query(Album).filter(Album.aid == path_pid).first()

                    if not album:
                        logger.error("相册不存在")
                        return ResponseFactory.success(data={
                            'message': 'pic.message.albumIsNone',
                            'messageType': 'error'
                        })

                    for pid in move_pic_list:
                        pic = db.query(Pic).filter(Pic.pid == pid).first()
                        if pic is not None:
                            pic.album_id = path_pid
                            db.commit()

                logger.info("移动图片成功")
                return ResponseFactory.success(data={
                    'message': 'pic.message.picMoveSuccess',
                    'messageType': 'success'
                })
            except Exception as e:
                logger.error(f"移动图片失败: {e}")
                return ResponseFactory.success(data={
                    'message': e,
                    'messageType': 'error'
                })