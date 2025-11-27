import os.path
import datetime

from flask import url_for
from werkzeug.utils import secure_filename

from manager.db_manager import get_session
from models.pic.pic import Pic
from models.pic.album import Album
from utils import ResponseFactory
from utils.basic.logging_utils import get_logger
from utils.file_utils import get_images_dir, generate_uuid_high_precision, get_image_info, get_app_dir, generate_thumbnail_pil

logger = get_logger(__name__)

# 图片上传服务类
class UploadService:
    @staticmethod
    def handle_upload(file, album_id):

        if file is None or album_id is None:
            logger.error(f"文件或相册ID为空，无法上传")
            return ResponseFactory.success(data={
                "message": 'upload.message.AlbumDoesNotExist',
                'messageType': 'error'
            })

        origin_file_path = None
        origin_file_id = None
        with get_session() as db:
            try:
                target_folder = db.query(Album).filter(
                    Album.aid == (1 if album_id == 0 else album_id)
                ).first()

                if target_folder is None:
                    # 相册不存在
                    logger.error(f"相册不存在，无法上传")
                    return ResponseFactory.success(data={
                        "message": 'upload.message.AlbumDoesNotExist',
                        'messageType': 'error'
                    })

                # 生成安全的文件名
                origin_filename = file.filename
                filename = secure_filename(file.filename)

                # 更改文件名称
                file_uuid = generate_uuid_high_precision(filename)
                file_suffix = os.path.splitext(filename)[1]

                # 生成日期路径
                today = datetime.datetime.today()
                relative_path = today.strftime("%Y/%m/%d")

                # 目标文件夹
                target_folder = os.path.join(get_images_dir(), relative_path)
                os.makedirs(target_folder, exist_ok=True)

                # 保存文件
                filename = file_uuid + file_suffix
                file_path = os.path.join(target_folder, filename)
                file.save(file_path)
                logger.info(f"文件保存成功，文件路径为: {file_path}")

                # 图片信息
                img_info = get_image_info(file_path)
                logger.info(img_info)

                # 数据库操作
                pic = Pic()
                pic.uuid = file_uuid
                pic.pic_name = filename
                pic.pic_original_name = origin_filename
                pic.pic_file_size = img_info.get('file_size')
                pic.pic_type = file.content_type
                pic.pic_size = img_info.get('dimensions')
                pic.pic_suffix = file_suffix
                pic.upload_time = datetime.datetime.now()
                pic.album_id = 1 if album_id == 0 else album_id
                pic.relative_path = relative_path
                pic.pic_desc = ''
                pic.pic_love = 0 if album_id != 0 else 1

                db.add(pic)
                db.commit()

                origin_file_path = file_path
                origin_file_id = pic.pid

                # 使用 url_for 自动生成完整 URL
                file_url = url_for("i.serve_file", filename=filename)

                # 生成缩略图
                images_folder = get_images_dir()
                thumbnail_folder = os.path.join(images_folder, 'thumbnail')
                if not os.path.exists(thumbnail_folder):
                    os.makedirs(thumbnail_folder, exist_ok=True, mode=0o777)

                output_path = os.path.join(thumbnail_folder, filename)
                generate_thumbnail_pil(file_path, output_path)

                # 缩略图 url
                thumbnail_url = url_for("i.serve_thumbnail", filename=filename)

                # 上传成功
                logger.info(f"图片上传成功，文件路径为: {file_path}")
                return ResponseFactory.success(data={
                    'filename': filename,
                    'url': file_url,
                    'thumbnail': thumbnail_url
                })

            except Exception as e:
                if origin_file_path is not None:
                    # 删除图片
                    os.remove(origin_file_path)
                    logger.info(f"删除文件: {origin_file_path}")

                if origin_file_id is not None:
                    # 删除数据库记录
                    db.query(Pic).filter(Pic.pid == origin_file_id).delete()
                    db.commit()

                logger.error(f"图片上传失败: {e}")
                return ResponseFactory.success(data={
                    "message": e,
                    'messageType': 'error'
                })