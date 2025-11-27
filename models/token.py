from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import declarative_base

TokenBase = declarative_base()

class Token(TokenBase):

    __tablename__ = 'tokens'

    tid = Column(Integer, primary_key=True)
    token = Column(String(200), unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=False, precision=0),
                        server_default=func.now())
    expires_at = Column(TIMESTAMP(timezone=False, precision=0),
                        server_default=func.now(),
                        nullable=False)
    is_active = Column(Boolean, default=True)

    def is_valid(self):
        """检查 Token 是否有效（未过期且激活）"""
        return self.is_active and self.expires_at > datetime.now()

    def to_dict(self):
        return {
            'tid': self.tid,
            'token': self.token,
            'userId': self.user_id,
            'createdAt': str(self.created_at),
            'expiresAt': str(self.expires_at),
            'isActive': self.is_active
        }