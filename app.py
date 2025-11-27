import os
import traceback
from datetime import timedelta

from manager.db_manager import init_database
from utils import app, load_config, ResponseFactory
from utils.basic.blueprint_utils import init_blueprint
from utils.basic.jwt_utils import init_jwt_config
from utils.basic.logging_utils import get_logger

logger = get_logger(__name__)

@app.errorhandler(Exception)
def handle_all_exceptions(error):
    error_traceback = traceback.format_exc()
    print("\033[91m" + "Error occurred:\n" + error_traceback + "\033[0m")
    return ResponseFactory.error(data=404).to_response()

@app.route('/')
def hello_ying_cang():
    logger.info("访问首页")
    return 'Hello Ying-Cang!'

if __name__ == '__main__':
    init_jwt_config()
    init_blueprint()

    config = load_config()

    # 如果数据库已配置直接连接
    if config["sql"]["host"] != 'none':
        init_database(config["sql"], 'postgresql')

    app.config["JWT_SECRET_KEY"] = config["server"]["key"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=config["server"]["tokenTime"])  # 设置为7天后过期

    app.run(host=config["server"]["host"],
            port=config["server"]["port"],
            debug=config["server"]["debug"])
