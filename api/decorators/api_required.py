from functools import wraps

from flask import request, jsonify

from manager.db_manager import get_session
from manager.token_manager import TokenManager
from models.config import Configs
from utils import ResponseFactory
from utils.basic.logging_utils import get_logger

logger = get_logger(__name__)

def token_required(f):
    @wraps(f)
    @check_api
    def decorated_function(*args, **kwargs):
        token_string = None

        # 从请求头获取 token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token_string = auth_header.split(' ')[1]

        # 从查询参数获取 token
        if not token_string:
            token_string = request.args.get('token')

        # 从表单数据获取 token
        if not token_string and request.json:
            token_string = request.json.get('token')

        if not token_string:
            return jsonify({
                'message': 'Token is missing'
            }), 401

        token = TokenManager.validate_token(token_string)
        if not token:
            return jsonify({
                'message': 'Invalid or expired token'
            }), 401

        # 将 token 信息添加到请求上下文中
        request.token = token

        return f(*args, **kwargs)

    return decorated_function

# 检测 api 接口是否开放
def check_api(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        with get_session() as db:
            use_api = True if db.query(Configs).filter_by(name='is_enable_api').first().value == '1' else False

            if not use_api:
                logger.error("API 未开放")
                return ResponseFactory.success(data={
                    'message': 'API is not open'
                }).to_response()

        return func(*args, **kwargs)
    return decorated_function