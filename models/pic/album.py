from sqlalchemy import Column, Integer, String, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import declarative_base

AlbumBase = declarative_base()


class Album(AlbumBase):
    __tablename__ = 'albums'

    aid = Column(Integer, primary_key=True)
    album_name = Column(String(200))
    created_at = Column(TIMESTAMP(timezone=False, precision=0),
                        server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=False, precision=0),
                        server_default=func.now(),
                        onupdate=func.now())

    def to_dict(self):
        return {
            'aid': self.aid,
            'albumName': self.album_name,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at
        }
