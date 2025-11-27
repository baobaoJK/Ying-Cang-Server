# 登录服务类
import urllib.parse

from flask_jwt_extended import create_access_token

from manager.user_manager import UserManager
from utils import ResponseFactory
from utils.basic.logging_utils import get_logger

logger = get_logger(__name__)
# 登录服务类
class LoginService:

    @staticmethod
    def login(username, password):

        # 用户名和密码为空返回
        if username is None or password is None:
            return ResponseFactory.success(data={
                'message': 'login.message.loginFailed',
                'messageType': 'error'
            })

        # 将 username 和 password 转为安全字符
        username = urllib.parse.quote(username)
        password = urllib.parse.quote(password)

        # 查询用户
        user_manager = UserManager()
        user = user_manager.authenticate_user(username, password)

        if not user:
            logger.error("用户名或密码错误")
            return ResponseFactory.success(data={
                'message': 'login.message.loginFailed',
                'messageType': 'error'
            })

        # 创建 JWT
        access_token = create_access_token(identity=str(1))
        logger.info("登录成功")
        return ResponseFactory.success(data={
            "token": access_token,
            'message': 'login.message.loginSuccess',
            'messageType': 'success'
        })