from argon2 import PasswordHasher, exceptions

from utils.basic.logging_utils import get_logger
from utils.config.load_config import load_config, save_config

# 初始化 Argon2
ph = PasswordHasher()

logger = get_logger(__name__)

# 用户管理
class UserManager:

    # 设置密码
    @staticmethod
    def set_password(password: str):
        logger.info("设置用户密码")
        hashed = ph.hash(password)
        config = load_config()
        config['server']['adminPassword'] = hashed
        save_config(config)

    # 验证密码
    @staticmethod
    def verify_password(password: str) -> bool:
        try:
            logger.info("验证用户密码")
            config = load_config()
            user_password = config['server']['adminPassword']
            return ph.verify(user_password, password)
        except exceptions.VerifyMismatchError:
            return False
        except exceptions.VerificationError:
            return False
        except exceptions.InvalidHash:
            return False

    # 验证用户登录
    def authenticate_user(self, username: str, password: str):
        config = load_config()

        if username == config['server']['adminAccount'] and self.verify_password(password):
                logger.info("用户信息验证通过")
                return True

        logger.info("用户信息验证失败")
        return False

    # 获取用户信息
    @staticmethod
    def get_user_info():
        config = load_config()
        return {
            'uid': 1,
            'username': config['server']['adminUsername'],
            'account': config['server']['adminAccount']
        }

    # 设置用户名
    @staticmethod
    def set_user_name(username):
        config = load_config()
        config['server']['adminUsername'] = username
        save_config(config)
        logger.info("设置用户名")
        return True

    # 设置密码
    @staticmethod
    def set_user_password(password):
        config = load_config()
        config['server']['adminPassword'] = ph.hash(password)
        save_config(config)
        logger.info("设置密码")
        return True