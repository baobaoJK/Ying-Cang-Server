from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models.config import ConfigsBase
from models.pic.pic import PicBase
from models.pic.album import AlbumBase
from models.token import TokenBase
from utils.basic.logging_utils import get_logger

logger = get_logger(__name__)

# 数据库管理类
class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._is_connected = False

    def connect_database(self, sql_config, db_type: str) -> bool:
        if self._is_connected:  # 使用状态标志而不是检查 engine
            return True

        # 数据库引擎和会话创建
        username = sql_config['username']  # 数据库用户名
        password = sql_config['password']  # 数据库密码
        host = sql_config['host']  # 数据库地址
        port = sql_config['port']  # 数据库端口
        database = sql_config['database']  # 数据库名称

        """连接数据库"""
        try:
            if db_type.lower() == 'postgresql':
                connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
            elif db_type.lower() == 'mysql':
                connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
                print(connection_string)
            else:
                raise ValueError("不支持的数据库类型")

            self.engine = create_engine(connection_string, echo=True, pool_pre_ping=True)

            # 测试连接
            with self.engine.begin() as conn:
                pass

            self.SessionLocal = scoped_session(
                sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            )
            logger.info(f"数据库连接成功，可以进行下一步")

            return True

        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False

    def create_tables(self) -> bool:
        """创建表（仅在连接成功后调用）"""
        if not self.engine:
            raise Exception("请先连接数据库")

        try:
            PicBase.metadata.create_all(bind=self.engine)
            AlbumBase.metadata.create_all(bind=self.engine)
            TokenBase.metadata.create_all(bind=self.engine)
            ConfigsBase.metadata.create_all(bind=self.engine)
            logger.info("表创建成功")
            return True
        except Exception as e:
            logger.error(f"表创建失败: {e}")
            return False

    def close(self):
        """关闭数据库连接"""
        if self.SessionLocal:
            self.SessionLocal.remove()
        if self.engine:
            self.engine.dispose()

# 创建全局单例实例
db_manager = DatabaseManager()

# 提供模块级别的便捷函数
def init_database(sql_config, db_type: str = 'postgresql') -> bool:
    """初始化数据库连接"""
    return db_manager.connect_database(sql_config, db_type)

@contextmanager
def get_session():
    """获取数据库会话"""
    if not db_manager.SessionLocal:
        raise Exception("请先调用 init_database() 初始化数据库连接")

    session = db_manager.SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()