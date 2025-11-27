import time
import uuid

from PIL import Image
import os
import sys

from utils import ResponseFactory
from utils.basic.logging_utils import get_logger

logger = get_logger(__name__)

# 获取本地文件夹
def get_app_dir():
    """获取 app.py 所在的目录，打包后也适用"""
    if getattr(sys, 'frozen', False):
        # 如果是 PyInstaller 打包后的程序
        base_dir = os.path.dirname(sys.executable)
    else:
        # 源码运行
        # base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return base_dir


# 获取上传图片文件夹
def get_images_dir():
    """获取 images 目录，如果没有则创建"""
    app_dir = get_app_dir()
    images_dir = os.path.join(app_dir, "images")
    os.makedirs(images_dir, exist_ok=True)  # 不存在则创建
    return images_dir


# 获取缩略图图片文件夹
def get_thumbnails_dir():
    """获取 thumbnails 目录，如果没有则创建"""
    images_dir = get_images_dir()
    thumbnails_dir = os.path.join(images_dir, "thumbnails")
    os.makedirs(thumbnails_dir, exist_ok=True)  # 不存在则创建
    return thumbnails_dir

# 获取 web-conf 文件夹
def get_web_conf_dir():
    """获取 web-conf 目录，如果没有则创建"""
    app_dir = get_app_dir()
    web_conf_dir = os.path.join(app_dir, "web-conf")
    os.makedirs(web_conf_dir, exist_ok=True)  # 不存在则创建
    return web_conf_dir


def generate_uuid_high_precision(filename: str) -> str:
    """根据文件名 + 当前毫秒级时间戳生成 UUID"""
    namespace = uuid.NAMESPACE_DNS
    timestamp = str(int(time.time() * 1000))  # 毫秒级时间戳
    unique_string = f"{filename}_{timestamp}"
    return str(uuid.uuid5(namespace, unique_string))


def get_image_info(image_path: str):
    """获取图片的文件大小（字节）和尺寸（像素）"""
    if not os.path.exists(image_path):
        return {"error": "文件不存在"}

    # 获取文件大小（字节）
    file_size = os.path.getsize(image_path)  # 无单位，单位为字节（Bytes）

    # 获取图片尺寸（像素）
    with Image.open(image_path) as img:
        width, height = img.size  # 图片尺寸（宽 x 高）

    return {
        "file_size": file_size,  # 文件大小（字节）
        "dimensions": f"{width}x{height}"  # 尺寸格式化输出
    }


# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif',
                      'bmp', 'webp', 'ico', 'jfif',
                      'tif', 'tga', 'svg'}

def allowed_file(filename, allowed_extensions=None):
    """检查文件扩展名是否允许"""
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS
    return "." in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# 判断文件方法
def check_file(files, allowed_extensions=None):
    if "file" not in files:
        logger.error("没有文件")
        return ResponseFactory.error(
            data={"message": "upload.message.noFiles"}
        ).to_response()

    file = files["file"]

    # 判断文件名是否位空
    if file.filename == "":
        logger.error("文件名为空")
        return ResponseFactory.error(
            data={"message": "upload.message.fileNameIsEmpty"}
        ).to_response()

    # 检查文件扩展名
    if not allowed_file(file.filename, allowed_extensions):
        logger.error("文件扩展名不允许")
        return ResponseFactory.error(
            data={"message": "upload.message.fileExtensionNotAllowed"}
        ).to_response()

    return None

# JPG/PNG 转 .ico
def convert_to_ico(input_path, output_path, sizes=None):
    """
    将图片转换为 ICO 格式

    Args:
        input_path: 输入图片路径 (JPG/PNG)
        output_path: 输出 ICO 文件路径
        sizes: ICO 图标尺寸列表，默认为 [16, 32, 48, 64]
    """
    if sizes is None:
        sizes = [16, 32, 48, 64]

    try:
        # 打开原始图片
        with Image.open(input_path) as img:
            # 转换为 RGBA（确保支持透明度）
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # 创建不同尺寸的图标
            icon_sizes = [(size, size) for size in sizes]

            # 保存为 ICO 格式
            img.save(output_path, format='ICO', sizes=icon_sizes)
            logger.info(f"成功转换: {input_path} -> {output_path}")

    except Exception as e:
        logger.error(f"转换失败: {e}")

# 生成 缩略图
def generate_thumbnail_pil(image_path, output_path, size=(250, 250)):
    logger.info(output_path)
    with Image.open(image_path) as image:
        image.thumbnail(size)
        image.save(output_path)