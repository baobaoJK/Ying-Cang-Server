from sqlalchemy import Column, Integer, String, BigInteger, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import declarative_base

PicBase = declarative_base()


class Pic(PicBase):
    __tablename__ = 'pics'

    pid = Column(Integer, primary_key=True)         # 图片 id
    uuid = Column(String(200))                      # 图片 uuid
    pic_name = Column(String(200))                  # 图片名称
    pic_original_name = Column(String(200))         # 图片原始名称
    pic_file_size = Column(BigInteger)              # 图片大小
    pic_type = Column(String(20))                   # 图片类型
    pic_size = Column(String(20))                   # 图片尺寸
    pic_suffix = Column(String(20))                 # 图片格式
    upload_time = Column(TIMESTAMP(timezone=False, precision=0),                  # 图片上传时间
                         server_default=text("CURRENT_TIMESTAMP(0)"))
    pic_desc = Column(String(200))                  # 图片描述
    album_id = Column(Integer)                      # 图片相册id
    pic_love = Column(Integer)                      # 图片是否最爱
    relative_path = Column(String(200))             # 图片相对路径

    def to_dict(self):
        return {
            'pid': self.pid,
            'uuid': self.uuid,
            'picName': self.pic_name,
            'picOriginalName': self.pic_original_name,
            'picFileSize': self.pic_file_size,
            'picType': self.pic_type,
            'picSize': self.pic_size,
            'picSuffix': self.pic_suffix,
            'uploadTime': str(self.upload_time),
            'picDesc': self.pic_desc,
            'albumId': self.album_id,
            'picLove': self.pic_love,
            'relativePath': self.relative_path
        }
