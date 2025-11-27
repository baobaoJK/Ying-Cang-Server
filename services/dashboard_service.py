import os
from collections import OrderedDict

import psutil
from pathlib import Path

from datetime import datetime, date, time, timedelta

from sqlalchemy import func

from manager.db_manager import get_session
from models.pic.album import Album
from models.pic.pic import Pic
from utils import ResponseFactory
from utils.basic.logging_utils import get_logger
from utils.file_utils import get_images_dir

logger = get_logger(__name__)

# 仪表盘服务类
class DashBoardService:
    """
    获取仪表盘数据
    """
    @staticmethod
    def get_dashboard_data():
        with get_session() as db:
            try:
                # 获取图片数量
                pic_count = db.query(Pic).count()

                # 获取今日上传图片数量
                today_start = datetime.combine(date.today(), time.min)
                today_pic_count = db.query(Pic).filter(Pic.upload_time >= today_start).count()

                # 获取本月上传图片数量
                today = date.today()
                month_start = date(today.year, today.month, 1)
                month_start_datetime = datetime.combine(month_start, time.min)
                month_pic_count = db.query(Pic).filter(Pic.upload_time >= month_start_datetime).count()

                # 获取相册数量
                album_count = db.query(Album).count()

                # 获取图库空间大小
                storage_info = get_storage_info(get_images_dir())

                # 获取图片类型
                result = db.query(
                    Pic.pic_suffix,
                    func.count(Pic.pid).label('count')
                ).group_by(Pic.pic_suffix).order_by(func.count(Pic.pid).desc()).all()
                # 转换为前端图表需要的格式
                chart_data = [
                    {'name': item.pic_suffix.replace('.', '').upper(), 'value': item.count}
                    for item in result
                ]

                # 获取近 30 天上传趋势
                upload_trend_data = get_upload_trend_for_chart(db)

                logger.info(f"获取仪表盘数据成功")
                return ResponseFactory.success(data={
                    'dashboard': {
                        'picCount': pic_count,
                        'todayPicCount': today_pic_count,
                        'monthPicCount': month_pic_count,
                        'albumCount': album_count
                    },
                    'storage': {
                        'totalSize': storage_info['total_size'],
                        'diskUsed': storage_info['disk_used'],
                        'freeSize': storage_info['free_size'],
                        'usedSize': storage_info['used_size'],
                    },
                    'imgPieData': chart_data,
                    'uploadTrend': upload_trend_data,
                    'messageType': 'success'
                })
            except Exception as e:
                logger.error(f"获取仪表盘数据失败：{e}")
                return ResponseFactory.success(data={
                    'message': e,
                    'messageType': 'error'
                })


def get_storage_info(image_folder_path):
    """
    获取图库存储信息
    Args:
        image_folder_path: 图片文件夹路径
    Returns:
        dict: 包含存储信息的字典
    """
    try:
        # 确保路径存在
        image_path = Path(image_folder_path)
        if not image_path.exists():
            raise FileNotFoundError(f"图片文件夹不存在: {image_folder_path}")

        # 获取文件夹所在磁盘分区
        disk_usage = psutil.disk_usage(str(image_path))

        # 计算图片文件夹大小
        folder_size = get_folder_size(image_path)

        logger.info(f"获取存储信息成功: {image_folder_path}")
        return {
            "total_size": disk_usage.total,  # 总大小（字节）
            "used_size": folder_size,  # 图库已用大小（字节）
            "free_size": disk_usage.free,  # 可用大小（字节）
            "disk_used": disk_usage.used  # 磁盘已用大小（字节）
        }

    except Exception as e:
        logger.error(f"获取存储信息失败: {e}")
        return {
            "total_size": 0,
            "used_size": 0,
            "free_size": 0,
            "disk_used": 0
        }

def get_folder_size(folder_path):
    """
    递归计算文件夹大小
    """
    total_size = 0
    try:
        for entry in os.scandir(folder_path):
            if entry.is_file():
                total_size += entry.stat().st_size
            elif entry.is_dir():
                total_size += get_folder_size(entry.path)
    except (PermissionError, OSError):
        # 处理权限问题或无法访问的文件
        pass
    logger.info(f"文件夹大小: {total_size}")
    return total_size

def get_upload_trend_30_days(db):
    """
    获取近30天上传趋势
    """
    # 计算日期范围
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=29)  # 包含今天共30天

    # 查询近30天每天的上传数量
    result = db.query(
        func.date(Pic.upload_time).label('upload_date'),
        func.count(Pic.pid).label('count')
    ).filter(
        Pic.upload_time >= start_date,
        Pic.upload_time < end_date + timedelta(days=1)  # 包含结束日期当天
    ).group_by(
        func.date(Pic.upload_time)
    ).order_by(
        func.date(Pic.upload_time)
    ).all()

    # 创建完整的30天数据（包括没有上传的日期）
    date_range = [start_date + timedelta(days=x) for x in range(30)]
    trend_data = OrderedDict()

    for single_date in date_range:
        trend_data[single_date.strftime('%Y-%m-%d')] = 0

    # 填充实际数据
    for item in result:
        date_str = item.upload_date.strftime('%Y-%m-%d')
        trend_data[date_str] = item.count

    logger.info(f"获取近30天上传趋势成功")
    return trend_data

def get_upload_trend_for_chart(db):
    """
    获取前端图表需要的格式
    """
    trend_data = get_upload_trend_30_days(db)

    # 转换为前端需要的格式
    dates = list(trend_data.keys())
    counts = list(trend_data.values())

    # 简化日期显示（只显示月份和日期）
    simplified_dates = [date_time[5:] for date_time in dates]  # 从 "2024-01-15" 变成 "01-15"

    return {
        "dates": simplified_dates,
        "counts": counts,
        "total_uploads": sum(counts)
    }