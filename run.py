from app import create_app, scheduler
from app.services import TaskService
from app.config import Config
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()

if __name__ == '__main__':
    # 设置应用实例到TaskService
    TaskService.set_app(app)
    logger.info("TaskService应用实例已设置")
    
    # 在应用上下文中启动调度器
    with app.app_context():
        logger.info("开始启动调度器...")
        TaskService.start_scheduler(app)
        logger.info(f"调度器启动完成，运行状态: {scheduler.running}")
        
        # 检查是否有任务
        jobs = scheduler.get_jobs()
        logger.info(f"当前调度器中的任务数量: {len(jobs)}")
        for job in jobs:
            logger.info(f"任务: {job.id} - {job.func}")
    
    # 使用配置文件中的参数运行Flask应用
    logger.info("启动Flask应用...")
    app.run(
        debug=Config.FLASK_DEBUG, 
        host=Config.FLASK_HOST, 
        port=Config.FLASK_PORT, 
        use_reloader=Config.FLASK_USE_RELOADER
    ) 