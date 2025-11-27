from sqlalchemy import Column, String, func, Integer
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

ConfigsBase = declarative_base()

class Configs(ConfigsBase):
    __tablename__ = 'configs'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    value = Column(String(1000))
    created_at = Column(TIMESTAMP(timezone=False, precision=0),
                        server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=False, precision=0),
                        server_default=func.now(),
                        onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at
        }
