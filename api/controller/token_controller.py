import urllib.parse

from flask import Blueprint, request

from api.decorators.api_required import token_required, check_api
from manager.token_manager import TokenManager
from manager.user_manager import UserManager
from utils import ResponseFactory
from utils.basic.logging_utils import get_logger

api_token_bp = Blueprint('api_token', __name__, url_prefix='/api/x')

logger = get_logger(__name__)

# 用户登录
@api_token_bp.route('/tokens', methods=['POST'])
@check_api
def tokens():
    data = request.json

    if data is None:
        logger.error("API 请求参数不能为空")
        return ResponseFactory.success(data={
            'message': '404'
        }).to_response()

    username = data.get('username', None)
    password = data.get('password', None)

    if username is None or password is None:
        logger.error("API 用户名或密码不能为空")
        return ResponseFactory.success(data={
            'message': 'username and password is required'
        }).to_response()

    logger.info("API 用户登录")

    username = urllib.parse.quote(username)
    password = urllib.parse.quote(password)

    # 查询用户
    user_manager = UserManager()
    user = user_manager.authenticate_user(username, password)

    if not user:
        logger.error("API 用户名或密码错误")
        return ResponseFactory.success(data={
            'message': 'username or password error'
        }).to_response()

    # 创建 token
    result = TokenManager.generate_token(1)

    if result['success']:
        token = result['token']
    else:
        logger.error("API 生成 token 失败")
        return ResponseFactory.error(data={
            'message': 'token generate error'
        }).to_response()

    logger.info("API 用户登录成功")
    return ResponseFactory.success(data={
        'token': token
    }).to_response()

# 清空 tokens
@api_token_bp.route('/tokens', methods=['DELETE'])
@token_required
def clear_tokens():
    logger.info("API 清空 tokens")
    result = TokenManager.cleanup_all_tokens()
    if result['success']:
        return ResponseFactory.success(data={
            'message': 'success'
        }).to_response()
    else:
        return ResponseFactory.error(data={
            'message': 'error'
        }).to_response()