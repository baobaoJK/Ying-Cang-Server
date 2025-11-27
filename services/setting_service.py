import os

from flask import url_for

from manager.db_manager import get_session
from manager.user_manager import UserManager
from models.config import Configs
from utils import ResponseFactory
from utils.basic.logging_utils import get_logger
from utils.file_utils import get_app_dir, convert_to_ico, get_web_conf_dir

logger = get_logger(__name__)

# 系统设置服务类
class SettingService:

    @staticmethod
    def get_web_setting():
        """获取网页设置信息"""

        with get_session() as db:
            try:
                web_config = db.query(Configs).all()

                # 把 web_config 拆分成 key:value
                web_config = {item.name: item.value for item in web_config}

                configs = {
                    'name': web_config.get('app_name'),
                    'appVersion': web_config.get('app_version'),
                    'webTitle': web_config.get('web_title'),
                    'mainTitle': web_config.get('main_title'),
                    'subTitle01': web_config.get('sub_title_01'),
                    'subTitle02': web_config.get('sub_title_02'),
                    'footerText': web_config.get('footer_text'),
                    'icpNo': web_config.get('icp_no'),
                    'useAPI': True if web_config.get('is_enable_api') == '1' else False,
                }

                logger.warning(f"获取网页设置信息成功: {configs}")

                web_logo_url = url_for('i.get_web_file', filename='logo.png')
                web_svg_logo_url = url_for('i.get_web_file', filename='logo.svg')
                web_login_bg_url = url_for('i.get_web_file', filename='login-bg.jpg')
                web_background_url = url_for('i.get_web_file', filename='background.jpg')
                return ResponseFactory.success(data={
                    'site': configs,
                    'webLogoUrl': web_logo_url,
                    'webSVGLogoUrl': web_svg_logo_url,
                    'webLoginBgUrl': web_login_bg_url,
                    'webBackgroundUrl': web_background_url
                })
            except Exception as e:
                logger.error(f"获取网页设置信息失败: {str(e)}")
                return ResponseFactory.error(data={
                    'message': e,
                    'messageType': 'error'})

    # 更新网页设置信息
    @staticmethod
    def update_web_setting(new_config, web_logo, web_svg_logo, web_login_bg, web_background):
        with get_session() as db:
            try:
                # 更改列表
                update_config = [
                    {'key': 'app_name', 'value': new_config.get('name', None)},
                    {'key': 'icp_no', 'value': new_config.get('icpNo', None)},
                    {'key': 'is_enable_api', 'value': new_config.get('useAPI', None)},
                    {'key': 'web_title', 'value': new_config.get('webTitle', None)},
                    {'key': 'main_title', 'value': new_config.get('mainTitle', None)},
                    {'key': 'sub_title_01', 'value': new_config.get('subTitle01', None)},
                    {'key': 'sub_title_02', 'value': new_config.get('subTitle02', None)},
                    {'key': 'footer_text', 'value': new_config.get('footerText', None)}
                ]

                for item in update_config:
                    if item['value'] is not None:
                        db.query(Configs).filter(Configs.name == item['key']).update({Configs.value: item['value']})

                app_folder = get_app_dir()

                # 更换网页 Logo
                if web_logo is not None:
                    web_logo.filename = "logo.png"
                    file_path = os.path.join(app_folder, 'web-conf', web_logo.filename)
                    web_logo.save(file_path)
                    convert_to_ico(file_path, os.path.join(app_folder, 'web-conf', 'favicon.ico'), [64])
                    logger.info("更换 Logo 成功")

                # 更换网页 SVG Logo
                if web_svg_logo is not None:
                    web_svg_logo.filename = "logo.svg"
                    file_path = os.path.join(app_folder, 'web-conf', web_svg_logo.filename)
                    web_svg_logo.save(file_path)
                    logger.info("更换 SVG Logo 成功")

                # 更新网页登录封面
                if web_login_bg is not None:
                    web_login_bg.filename = "login-bg.jpg"
                    file_path = os.path.join(app_folder, 'web-conf', web_login_bg.filename)
                    web_login_bg.save(file_path)
                    logger.info("更换登录封面成功")

                # 更换网页背景图片
                if web_background is not None:
                    web_background.filename = "background.jpg"
                    file_path = os.path.join(app_folder, 'web-conf', web_background.filename)
                    web_background.save(file_path)
                    logger.info("更换背景图片成功")

                return ResponseFactory.success(data={'messageType': 'success'})
            except Exception as e:
                logger.error(f"获取网页设置信息失败: {str(e)}")
                return ResponseFactory.error(data={
                    'message': e,
                    'messageType': 'error'})

    # 获取用户设置信息
    @staticmethod
    def get_user_setting():
        with get_session() as db:
            try:
                user_manager = UserManager()
                user = user_manager.get_user_info()

                # 获取用户头像
                web_conf_folder = get_web_conf_dir()
                user_avatar_url = ''
                for ext in ['png', 'jpg', 'jpeg', 'gif']:
                    avatar_file = os.path.join(web_conf_folder, f'avatar.{ext}')
                    if os.path.exists(avatar_file):
                        user_avatar_url = url_for('i.get_web_file', filename=f'avatar.{ext}')
                        break
                return ResponseFactory.success(data={
                    'username': user.get('username'),
                    'account': user.get('account'),
                    'userAvatarUrl': user_avatar_url})
            except Exception as e:
                logger.error(f"获取用户设置信息失败: {str(e)}")
                return ResponseFactory.error(data={
                    'message': e,
                    'messageType': 'error'})

    # 更新用户设置信息
    @staticmethod
    def update_user_setting(avatar_img, user_name, pass_word):
        if avatar_img is not None:
            try:
                # 删除旧头像
                web_conf_folder = get_web_conf_dir()
                for ext in ['png', 'jpg', 'jpeg', 'gif']:
                    avatar_file = os.path.join(web_conf_folder, f'avatar.{ext}')
                    if os.path.exists(avatar_file):
                        os.remove(avatar_file)

                # 获取文件名的后缀
                ext = avatar_img.filename.split('.')[-1]
                # 设置文件名
                avatar_img_name = 'avatar.' + ext
                # 保存文件
                app_folder = get_app_dir()
                file_path = os.path.join(app_folder, 'web-conf', avatar_img_name)
                avatar_img.save(file_path)
                logger.info("更换头像成功")
            except Exception as e:
                logger.error(f"更换头像失败: {str(e)}")
                return ResponseFactory.error(data={
                    'message': e,
                    'messageType': 'error'})

        if user_name is not None:
            user_manager = UserManager()
            user_manager.set_user_name(user_name)
            logger.info("修改用户名成功")

        if pass_word is not None:
            user_manager = UserManager()
            user_manager.set_user_password(pass_word)
            logger.info("修改密码成功")

        return ResponseFactory.success(data={'messageType': 'success'})
