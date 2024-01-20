import os
import json

config_file = f'./config.json'
default_config_dict = {
    'host': '127.0.0.1',
    'port': 9500,
    'log_file': 'fk-latest.log',
    'version_check_url': 'https://gitee.com/notify-ctrl/FreeKill/releases/latest',
    # 'version_check_url': 'https://github.com/Qsgs-Fans/FreeKill/releases/latest',
    'backup_directory': 'backups',
    'backup_ignore': [
        '.git',
        '.github',
        'build',
    ],
    'custom_trans': {
        'mobile_effect': '手杀特效',
        'utility': '常用函数',
    },
    'server_dict': {},
}

# 配置类
class Config:

    def __init__(self) -> None:
        self.initConfig()
        self.raw = self.read()
        self.host = self.raw.get('host')
        self.port = self.raw.get('port')
        self.log_file = self.raw.get('log_file')
        self.version_check_url = self.raw.get('version_check_url')
        self.backup_directory = self.raw.get('backup_directory')
        self.backup_ignore = self.raw.get('backup_ignore')
        self.custom_trans = self.raw.get('custom_trans')
        self.server_dict = self.raw.get('server_dict')
        self.verify()

    # 初始化配置文件
    def initConfig(self):
        try:
            open(config_file)
        except:
            json.dump(default_config_dict, open(config_file, 'w'), ensure_ascii=False, indent=2)

    # 获取指定配置
    def read(self, key: str=None) -> list | dict | str | int | bool:
        json_data = json.load(open(config_file))
        if key:
            json_data = json.load(open(config_file)).get(key)
        return json_data

    # 保存指定配置文件
    def save(self, key: str, value: list | dict | str | int | bool) -> str:
        try:
            json_data = json.load(open(config_file))
            json_data[key] = value
            json.dump(json_data, open(config_file, 'w'), ensure_ascii=False, indent=2)
        except Exception as e:
            return f'保存配置文件发生错误\n {e}'
        return ''

    # 验证配置文件的完整性
    def verify(self):
        value = None
        if self.host is None:
            key = "host"
            value = default_config_dict[key]
            self.save(key, value)
            self.host = value
        if self.port is None:
            key = "port"
            value = default_config_dict[key]
            self.save(key, value)
            self.port = value
        if self.log_file is None:
            key = "log_file"
            value = default_config_dict[key]
            self.save(key, value)
            self.log_file = value
        if self.version_check_url is None:
            key = "version_check_url"
            value = default_config_dict[key]
            self.save(key, value)
            self.version_check_url = value
        if self.backup_directory is None:
            key = "backup_directory"
            value = default_config_dict[key]
            self.save(key, value)
            self.backup_directory = value
        if self.backup_ignore is None:
            key = "backup_ignore"
            value = default_config_dict[key]
            self.save(key, value)
            self.backup_ignore = value
        if self.custom_trans is None:
            key = "custom_trans"
            value = default_config_dict[key]
            self.save(key, value)
            self.custom_trans = value
        if self.server_dict is None:
            key = "server_dict"
            value = default_config_dict[key]
            self.save(key, value)
            self.server_dict = value
        if value:
            self.raw = self.read()