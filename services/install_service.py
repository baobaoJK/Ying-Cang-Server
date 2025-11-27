from manager.db_manager import db_manager, init_database, get_session
from manager.user_manager import UserManager
from models.config import Configs
from services.pic.album_service import AlbumService
from utils import load_config, save_config
from utils.basic.logging_utils import get_logger
from utils.response_utils import ResponseFactory

logger = get_logger(__name__)

# 项目安装服务类
class InstallService:

    # 检查是否第一次安装
    @staticmethod
    def check_install():
        config = load_config()
        return ResponseFactory.success(config['sql']['host'] == 'none')

    # 填写配置信息
    @classmethod
    def config_install(cls, sql_data):
        config = load_config()

        if config.get('sql', {}).get('host') != 'none':
            return ResponseFactory.success(data={
                "message": "server is completely installed"
            })

        # 获取数据库类型
        db_type = sql_data.get('sqlType', None)

        # 检查是否能连接数据库
        if db_manager.connect_database(sql_data, db_type):
            # 初始化数据库
            init_database(sql_data, db_type)
            try:
                # 创建数据表
                if db_manager.create_tables():
                    # 创建默认相册
                    pic_folder_service = AlbumService()
                    pic_folder_service.create_album('default')

                    # 创建网页信息
                    with get_session() as db:
                        try:
                            config = load_config()

                            # 网页信息
                            config_data = {
                                "app_name": "影仓",
                                "app_version": config['server']['version'],
                                "icp_no": "",
                                "is_enable_api": "1",
                                "main_title": "私人安全影像仓库",
                                "sub_title_01": "上传您的图片，可存储不同格式的图片以及视频",
                                "sub_title_02": "可以使用 APP 将影像分享至 QQ 或 微信",
                                "web_title": "影仓-您的私人安全影像仓库",
                                "footer_text": "Copyright © 2025 - Present Ying-Cang. All rights reserved.",
                            }

                            for name, value in config_data.items():
                                config = Configs(name=name, value=value)
                                db.add(config)

                            db.commit()
                        except Exception as e:
                            db.rollback()
                            logger.error(f"初始化配置失败: {e}")

                    logger.info("创建用户，文件夹，基础信息成功")

                    # 保存数据库连接信息
                    config = load_config()
                    config['server']['adminAccount'] = sql_data.get('account')
                    config['sql']['host'] = sql_data.get('host')
                    config['sql']['port'] = sql_data.get('port')
                    config['sql']['username'] = sql_data.get('username')
                    config['sql']['password'] = sql_data.get('password')
                    config['sql']['database'] = sql_data.get('database')
                    save_config(config)

                    user_manager = UserManager()
                    user_manager.set_password(sql_data.get('userPassword'))

                    return ResponseFactory.success(data={
                            'message': 'install.message.success',
                            'messageType': 'success'
                        })
                else:
                    logger.error("创建数据表失败")
                    return ResponseFactory.success(data={
                        'message': 'install.message.createSQLTableFailed',
                        'messageType': 'error'
                    })
            except Exception as e:
                logger.error(f"创建表格、用户失败: {str(e)}")
                return ResponseFactory.success(data={
                    'message': 'install.message.createSQLFailed',
                    'messageType': 'error'
                })
        else:
            logger.error("连接数据库失败")
            return ResponseFactory.success(data={
                    'message': 'install.message.sqlConnectFailed',
                    'messageType': 'error'
                })
