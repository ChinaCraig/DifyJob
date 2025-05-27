from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化扩展
db = SQLAlchemy()
scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__)
    
    # 配置数据库
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:19900114xin@192.168.16.105:3306/wechat_job'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # 初始化扩展
    db.init_app(app)
    
    # 注册蓝图
    from app.routes import main
    app.register_blueprint(main)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app 