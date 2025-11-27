from functools import wraps

from flask import request

from utils import ResponseFactory

# 装饰器，用于判断是否为浏览器访问
def browser_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_agent = request.headers.get('User-Agent', '')
        if 'Mozilla' not in user_agent:
            return ResponseFactory.error(data='404').to_response()
        return f(*args, **kwargs)
    return decorated_function
