# config.py
import yaml
import os


class ConfigError(Exception):
    pass


class Config:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.data = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            raise ConfigError(f"配置文件不存在: {self.path}")
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            self._validate(data)
            return data
        except Exception as e:
            raise ConfigError(f"配置文件加载失败: {e}")

    def _validate(self, data):
        if not isinstance(data, dict):
            raise ConfigError("配置文件格式错误，应为字典")
        device = data.get("device")
        if not device or not isinstance(device, dict):
            raise ConfigError("缺少 device 节点或格式错误")
        for key in ("ip", "username", "password", "login_retry"):
            if key not in device:
                raise ConfigError(f"device 配置缺少字段: {key}")

        log = data.get("log")
        if not log or not isinstance(log, dict):
            raise ConfigError("缺少 log 节点或格式错误")
        for key in ("name", "log_file", "level", "max_bytes", "backup_count"):
            if key not in log:
                raise ConfigError(f"log 配置缺少字段: {key}")

        api_server = data.get("api_server")
        if not api_server or not isinstance(api_server, dict):
            raise ConfigError("缺少 api_server 节点或格式错误")
        for key in ("port", "api_token","enabled"):
            if key not in api_server:
                raise ConfigError(f"api_server 配置缺少字段: {key}")

    def get_device_config(self):
        return self.data.get("device", {})

    def get_log_config(self):
        return self.data.get("log", {})

    def get_logger_name(self):
        return self.data.get("log", {}).get("name")

    def get_api_server_config(self):
        return self.data.get("api_server")

    def get_api_token(self):
        return self.data.get("api_server", {}).get("api_token")