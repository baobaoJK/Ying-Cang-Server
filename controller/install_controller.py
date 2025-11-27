from flask import Blueprint, request

from decorators.browser_decorators import browser_only
from services.install_service import InstallService
from utils.basic.logging_utils import get_logger

install_bp = Blueprint('install', __name__, url_prefix='/api')

logger = get_logger(__name__)

# 检查是否第一次安装
@install_bp.route('/install/check')
@browser_only
def check_install():
    init_install = InstallService.check_install()
    logger.info("检查是否第一次安装")
    return init_install.to_response()

# 填写配置信息
@install_bp.route('/install/config', methods=['POST'])
@browser_only
def config_install():
    data = request.json
    config = InstallService.config_install(data)
    logger.info("填写配置信息")
    return config.to_response()