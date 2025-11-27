from flask import Blueprint
from flask_jwt_extended import jwt_required

from services.dashboard_service import DashBoardService
from utils.basic.logging_utils import get_logger

# 声明地址
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api')

# 仪表盘服务类
dashboard_service = DashBoardService()

logger = get_logger(__name__)

# 获取仪表盘数据
@dashboard_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    result = dashboard_service.get_dashboard_data()
    logger.info("获取仪表盘数据")
    return result.to_response()