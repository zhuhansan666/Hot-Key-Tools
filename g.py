from config import Config
from log import Logging
from app_config import AppConfig
app_config = AppConfig()


config = Config(app_config.config_file)
config.load()
logging = Logging(log_file=app_config.log_file)
