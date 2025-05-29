import os
import logging
from logging.handlers import RotatingFileHandler
from app.config import Config

def setup_logging(app):
    """设置应用日志配置"""
    
    # 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 应用日志文件路径
    app_log_file = os.path.join(log_dir, "app.log")
    
    # 创建日志处理器
    file_handler = RotatingFileHandler(
        app_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    
    # 设置日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # 设置日志级别
    file_handler.setLevel(Config.get_log_level())
    
    # 添加处理器到应用
    app.logger.addHandler(file_handler)
    app.logger.setLevel(Config.get_log_level())
    
    # 设置 Werkzeug 日志
    werkzeug_log_file = os.path.join(log_dir, "werkzeug.log")
    werkzeug_handler = RotatingFileHandler(
        werkzeug_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    werkzeug_handler.setFormatter(formatter)
    logging.getLogger('werkzeug').addHandler(werkzeug_handler)
    
    # 设置 SQLAlchemy 日志
    sqlalchemy_log_file = os.path.join(log_dir, "sqlalchemy.log")
    sqlalchemy_handler = RotatingFileHandler(
        sqlalchemy_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    sqlalchemy_handler.setFormatter(formatter)
    logging.getLogger('sqlalchemy').addHandler(sqlalchemy_handler)
    
    # 设置 APScheduler 日志
    scheduler_log_file = os.path.join(log_dir, "scheduler.log")
    scheduler_handler = RotatingFileHandler(
        scheduler_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    scheduler_handler.setFormatter(formatter)
    logging.getLogger('apscheduler').addHandler(scheduler_handler) 