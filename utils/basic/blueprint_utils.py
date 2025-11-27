from utils import app

from api.controller.album_controller import api_album_bp
from api.controller.token_controller import api_token_bp
from api.controller.pic_controller import api_upload_bp
from controller.dashboard_controller import dashboard_bp
from controller.install_controller import install_bp
from controller.login_controller import login_bp
from controller.pic.pic_controller import pic_bp
from controller.pic.pic_file_controller import pic_file_bp
from controller.pic.album_controller import album_bp
from controller.pic.upload_controller import upload_bp
from controller.setting_controller import setting_bp
from utils.basic.logging_utils import get_logger

logger = get_logger(__name__)

def init_blueprint():
    logger.info("初始化 BluePrint")
    # web blueprint
    app.register_blueprint(install_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(pic_bp)
    app.register_blueprint(album_bp)
    app.register_blueprint(pic_file_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(setting_bp)

    # api blueprint
    app.register_blueprint(api_token_bp)
    app.register_blueprint(api_upload_bp)
    app.register_blueprint(api_album_bp)