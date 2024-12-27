import os
import configparser
import re

class ConfigReader:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.expanduser("~/.pymdb_client")
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

    def load_from_env(self, value):
        if value and value.startswith('${') and value.endswith('}'):
            env_var = re.match(r'\${(.*)}', value).group(1)
            return os.getenv(env_var, value)
        elif value:
            return value
        else:
            return None

    def get_base_url(self):
        base_url = self.config.get('pymdb_client', 'base_url', fallback=None)
        return self.load_from_env(base_url)

    def get_user_token(self):
        user_token = self.config.get('pymdb_client', 'user_token', fallback=None)
        return self.load_from_env(user_token)
    
    def get_app_token(self):
        app_token = self.config.get('pymdb_client', 'app_token', fallback=None)
        return self.load_from_env(app_token)
