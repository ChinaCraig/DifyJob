from app import create_app, scheduler
from app.services import TaskService
from app.config import Config

app = create_app()

if __name__ == '__main__':
    # 设置应用实例到TaskService
    TaskService.set_app(app)
    
    # 在应用上下文中启动调度器
    with app.app_context():
        TaskService.start_scheduler(app)
    
    # 使用配置文件中的参数运行Flask应用
    app.run(
        debug=Config.FLASK_DEBUG, 
        host=Config.FLASK_HOST, 
        port=Config.FLASK_PORT, 
        use_reloader=Config.FLASK_USE_RELOADER
    ) 