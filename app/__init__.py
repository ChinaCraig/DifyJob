from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import Config

# 初始化扩展
db = SQLAlchemy()
scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__)
    
    # 使用配置类
    app.config.from_object(Config)
    
    # 初始化扩展
    db.init_app(app)
    
    # 注册蓝图
    from app.routes import main
    app.register_blueprint(main)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app 