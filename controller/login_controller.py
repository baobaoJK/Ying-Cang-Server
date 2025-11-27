from flask import request
from flask import Blueprint

from decorators.browser_decorators import browser_only
from services.login_service import LoginService
from utils import ResponseFactory
from utils.basic.app_instance import limiter
from utils.basic.logging_utils import get_logger

login_bp = Blueprint('login', __name__, url_prefix='/api')

login_service = LoginService()

logger = get_logger(__name__)

# 用户登录
@login_bp.route('/login', methods=['POST'])
@browser_only
@limiter.limit("5 per hour")  # 每小时最多5次
def login():
    data = request.json

    if data is None:
        return ResponseFactory.error(data='404').to_response()

    username = data.get('username', None)
    password = data.get('password', None)

    if username is None or password is None:
        return ResponseFactory.error(data='404').to_response()

    logger.info("用户登录")
    result = login_service.login(username, password)

    return result.to_response()
