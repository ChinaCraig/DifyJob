import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('config.env')

class Config:
    """应用配置类"""
    
    # Flask基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Flask运行配置
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5001))
    FLASK_USE_RELOADER = os.getenv('FLASK_USE_RELOADER', 'False').lower() == 'true'
    
    # 数据库配置
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'wechat_job')
    
    # 构建数据库URI
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Dify配置
    DIFY_API_URL = os.getenv('DIFY_API_URL', 'http://localhost/v1/workflows/run')
    DIFY_API_KEY = os.getenv('DIFY_API_KEY', '')
    DIFY_API_TIMEOUT = int(os.getenv('DIFY_API_TIMEOUT', 30))
    DIFY_USER_IDENTIFIER = os.getenv('DIFY_USER_IDENTIFIER', 'wechat-job-system')
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # 分页配置
    LOGS_PER_PAGE_DEFAULT = int(os.getenv('LOGS_PER_PAGE_DEFAULT', 10))
    LOGS_PER_PAGE_MAX = int(os.getenv('LOGS_PER_PAGE_MAX', 50))
    
    # 自动刷新配置
    AUTO_REFRESH_INTERVAL_SECONDS = int(os.getenv('AUTO_REFRESH_INTERVAL_SECONDS', 30))
    NEAR_EXECUTION_REFRESH_SECONDS = int(os.getenv('NEAR_EXECUTION_REFRESH_SECONDS', 5))
    
    @classmethod
    def get_log_level(cls):
        """获取日志级别"""
        import logging
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return level_map.get(cls.LOG_LEVEL.upper(), logging.INFO) 