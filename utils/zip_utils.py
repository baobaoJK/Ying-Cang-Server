import os
import zipfile

from flask import send_file
from werkzeug.utils import secure_filename

import globals as g
from utils import ResponseFactory
from utils.basic.logging_utils import get_logger
from utils.file_utils import get_images_dir, get_app_dir

IMAGE_DIR = get_images_dir()
THUMBNAIL_DIR = os.path.join(get_images_dir(), "thumbnail")
UPLOAD_FILE_DIR = os.path.join(get_app_dir(), "upload")
ZIP_PATH = os.path.join(UPLOAD_FILE_DIR, "images.zip")

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)
os.makedirs(UPLOAD_FILE_DIR, exist_ok=True)

logger = get_logger(__name__)

# 压缩图片
def generate_zip():
    g.zip_progress = 0

    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)

    files_to_zip = []
    for root, dirs, files in os.walk(IMAGE_DIR):
        for f in files:
            files_to_zip.append(os.path.join(root, f))
    total = len(files_to_zip)
    if total == 0:
        g.zip_progress = 100
        return

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for idx, file_path in enumerate(files_to_zip, 1):
            arcname = os.path.relpath(file_path, IMAGE_DIR)
            zf.write(file_path, arcname=arcname)
            g.zip_progress = int(idx / total * 100)

def download_zip():
    if not os.path.exists(ZIP_PATH):
        logger.error("ZIP 文件不存在 无法下载")
        return ResponseFactory.error(data={
            'message': 'setting.fileManager.message.zipFileIsNotExists',
            'messageType': 'error'
        }).to_response()
    return send_file(
        ZIP_PATH,
        mimetype="application/zip",
        as_attachment=True,
        download_name="images.zip"
    )

# 解压
def unzip(file):
    filename = secure_filename(file.filename)
    zip_path = os.path.join(UPLOAD_FILE_DIR, filename)
    file.save(zip_path)

    # 解压
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for member in zip_ref.namelist():
            # 确定路径
            member_path = os.path.normpath(member)
            if member_path.startswith("thumbnail/"):
                target_path = os.path.join(THUMBNAIL_DIR, member_path.replace("thumbnail/", ""))
            else:
                target_path = os.path.join(IMAGE_DIR, member_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with zip_ref.open(member) as source, open(target_path, "wb") as target:
                target.write(source.read())
    # 删除
    os.remove(zip_path)

    logger.info("图片导入成功")
    return ResponseFactory.success(data={
        "message": "setting.fileManager.message.importImagesSuccess",
        "messageType": "success"
    }).to_response()