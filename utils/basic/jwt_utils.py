from flask_jwt_extended import JWTManager
from flask import jsonify
from utils import app
from utils.basic.logging_utils import get_logger

logger = get_logger(__name__)

def init_jwt_config():
    logger.info("初始化 JWT")
    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        # return jsonify({"msg": "Token has expired", "code": "token_expired"}), 401
        return jsonify({"message": "token.expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        # return jsonify({"msg": "Invalid token", "code": "invalid_token"}), 401
        return jsonify({"message": "token.invalid"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        # return jsonify({"msg": "Missing token", "code": "authorization_required"}), 401
        return jsonify({"message": "token.missing"}), 401
