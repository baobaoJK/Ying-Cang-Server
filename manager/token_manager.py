import secrets
from datetime import datetime, timedelta

from manager.db_manager import get_session
from models.token import Token
from utils.basic.logging_utils import get_logger

logger = get_logger(__name__)

class TokenManager:
    @staticmethod
    def generate_token(user_id, expires_days=30):
        with get_session() as db:
            """生成新的 token"""
            try:
                # 先使该用户的所有旧 token 失效
                TokenManager.revoke_user_tokens(user_id)

                # 创建新 token
                new_token = Token()
                new_token.user_id = user_id
                new_token.token = secrets.token_urlsafe(32)
                new_token.expires_at = datetime.now() + timedelta(days=expires_days)
                db.add(new_token)
                db.commit()

                logger.info("生成新 Token")
                return {
                    'success': True,
                    'token': new_token.token,
                    'expiresAt': new_token.expires_at.isoformat(),
                    'userId': user_id
                }
            except Exception as e:
                db.rollback()
                logger.error(f"生成新 Token 失败: {str(e)}")
                return {'success': False, 'error': str(e)}

    @staticmethod
    def validate_token(token_string):
        """验证 token 是否有效"""
        if not token_string:
            logger.info("无效的 Token")
            return None

        with get_session() as db:
            token = db.query(Token).filter_by(token=token_string, is_active=True).first()

            if token and token.is_valid():
                logger.info("Token 验证成功")
                return token
            logger.info("无效的 Token")
            return None

    @staticmethod
    def revoke_token(token_string):
        """撤销单个 token"""
        with get_session() as db:
            try:
                token = db.query(Token).filter_by(token=token_string).first()
                if token:
                    token.is_active = False
                    db.commit()
                    logger.info("Token 撤销成功")
                    return {'success': True, 'message': 'Token revoked successfully'}
                logger.info("Token 不存在")
                return {'success': False, 'error': 'Token not found'}
            except Exception as e:
                db.rollback()
                logger.error(f"Token 撤销失败: {str(e)}")
                return {'success': False, 'error': str(e)}

    @staticmethod
    def revoke_user_tokens(user_id):
        with get_session() as db:
            """撤销用户的所有 token"""
            try:
                tokens = db.query(Token).filter_by(user_id=user_id, is_active=True).all()
                for token in tokens:
                    token.is_active = False
                db.commit()
                logger.info("用户所有 Token 撤销成功")
                return {'success': True, 'message': f'All tokens for user {user_id} revoked'}
            except Exception as e:
                db.rollback()
                logger.error(f"用户所有 Token 撤销失败: {str(e)}")
                return {'success': False, 'error': str(e)}

    @staticmethod
    def get_user_tokens(user_id):
        with get_session() as db:
            """获取用户的所有 token"""
            tokens = db.query(Token).filter_by(user_id=user_id).order_by(Token.created_at.desc()).all()
            logger.info("获取用户所有 Token 成功")
            return [token.to_dict() for token in tokens]

    @staticmethod
    def cleanup_expired_tokens():
        with get_session() as db:
            """清理过期的 token"""
            try:
                expired_tokens = db.query(Token).filter(
                    Token.expires_at < datetime.now()
                ).all()

                for token in expired_tokens:
                    db.delete(token)

                db.commit()
                logger.info("清理过期 Token 成功")
                return {'success': True, 'cleaned_count': len(expired_tokens)}
            except Exception as e:
                db.rollback()
                logger.error(f"清理过期 Token 失败: {str(e)}")
                return {'success': False, 'error': str(e)}

    @staticmethod
    def cleanup_all_tokens():
        with get_session() as db:
            """清理所有 token"""
            try:
                tokens = db.query(Token).all()
                for token in tokens:
                    db.delete(token)

                db.commit()
                logger.info("清理所有 Token 成功")
                return {'success': True, 'cleaned_count': len(tokens)}
            except Exception as e:
                db.rollback()
                logger.error(f"清理所有 Token 失败: {str(e)}")
                return {'success': False, 'error': str(e)}