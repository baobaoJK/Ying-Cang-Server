import os.path

import yaml

CONFIG_FILE = "./config/config.yaml"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        config_content = os.path.expandvars(file.read())
        config_yaml = yaml.safe_load(config_content)  # 安全加载 YAML
    return config_yaml


def save_config(data):
    """保存配置到 YAML 文件"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        print("保存文件 YAML")
        yaml.dump(data, file, allow_unicode=True,
                              default_flow_style=False,
                              sort_keys=False,
                              default_style='"')
