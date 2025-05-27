from app import create_app, scheduler
from app.services import TaskService

app = create_app()

if __name__ == '__main__':
    # 设置应用实例到TaskService
    TaskService.set_app(app)
    
    # 在应用上下文中启动调度器
    with app.app_context():
        TaskService.start_scheduler(app)
    
    # 运行Flask应用
    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False) 