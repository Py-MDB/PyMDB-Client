import os
import configparser
import re

class ConfigReader:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.expanduser("~/.pymdb_client")
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

    def get_base_url(self):
        base_url = self.config.get('pymdb_client', 'base_url', fallback=None)
        if base_url and base_url.startswith('${') and base_url.endswith('}'):
            env_var = re.match(r'\${(.*)}', base_url).group(1)
            base_url = os.getenv(env_var, base_url)
        return base_url
