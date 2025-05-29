import requests
import json
from datetime import datetime, timedelta
from app import db, scheduler
from app.config import Config
import logging

# 配置日志
logging.basicConfig(level=Config.get_log_level())
logger = logging.getLogger(__name__)

class TaskService:
    """任务服务类"""
    
    @staticmethod
    def call_dify_api(start_time, end_time, api_key, api_url):
        """调用Dify API"""
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "inputs": {
                    "start_time": start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "end_time": end_time.strftime('%Y-%m-%d %H:%M:%S')
                },
                "response_mode": "streaming",
                "user": Config.DIFY_USER_IDENTIFIER
            }
            
            response = requests.post(api_url, headers=headers, json=data, timeout=Config.DIFY_API_TIMEOUT)
            response.raise_for_status()
            
            return True, response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Dify API调用失败: {str(e)}")
            return False, str(e)
        except Exception as e:
            logger.error(f"未知错误: {str(e)}")
            return False, str(e)
    
    # 存储应用实例的类变量
    _app = None
    
    @classmethod
    def set_app(cls, app):
        """设置应用实例"""
        cls._app = app
    
    @staticmethod
    def execute_task(force=False):
        """执行定时任务"""
        logger.info("execute_task 被调用")
        app = TaskService._app
        if not app:
            logger.error("应用实例未设置")
            return
            
        with app.app_context():
            try:
                from app.models import TaskLog, TaskConfig
                # 获取任务配置
                config = TaskConfig.query.first()
                logger.info(f"获取到配置: config={config}, is_active={config.is_active if config else None}")
                
                if not config:
                    logger.info("配置不存在")
                    return
                
                # 如果不是强制执行，检查任务是否启用
                if not force and not config.is_active:
                    logger.info("任务未启用或配置不存在")
                    return
                
                logger.info("开始执行任务...")
                
                # 计算时间范围
                if config.last_end_time:
                    start_time = config.last_end_time
                else:
                    start_time = datetime.now() - timedelta(minutes=config.interval_minutes)
                
                end_time = start_time + timedelta(minutes=config.interval_minutes)
                execute_time = datetime.now()
                
                logger.info(f"时间范围: {start_time} -> {end_time}")
                
                # 调用Dify API
                success, response_data = TaskService.call_dify_api(
                    start_time, end_time, config.dify_api_key, config.dify_url
                )
                
                # 记录日志
                task_log = TaskLog(
                    interval_minutes=config.interval_minutes,
                    execute_time=execute_time,
                    start_time=start_time,
                    end_time=end_time,
                    status='success' if success else 'failed',
                    response_data=response_data if success else None,
                    error_message=response_data if not success else None
                )
                
                db.session.add(task_log)
                
                # 更新配置中的最后结束时间
                config.last_end_time = end_time
                config.updated_at = datetime.now()
                
                db.session.commit()
                
                logger.info(f"任务执行完成: {start_time} -> {end_time}, 状态: {'成功' if success else '失败'}")
                
            except Exception as e:
                logger.error(f"任务执行异常: {str(e)}")
                import traceback
                logger.error(f"详细错误: {traceback.format_exc()}")
                try:
                    db.session.rollback()
                except Exception as rollback_error:
                    logger.error(f"回滚失败: {str(rollback_error)}")
    
    @staticmethod
    def start_scheduler(app):
        """启动调度器"""
        if not scheduler.running:
            scheduler.start()
            logger.info("调度器已启动")
        
        # 检查是否有活跃的任务配置
        with app.app_context():
            from app.models import TaskConfig
            config = TaskConfig.query.first()
            if config and config.is_active:
                TaskService.schedule_task(config.interval_minutes)
    
    @staticmethod
    def schedule_task(interval_minutes):
        """调度任务"""
        try:
            # 移除现有的任务
            if scheduler.get_job('dify_task'):
                scheduler.remove_job('dify_task')
            
            # 移除可能存在的一次性任务
            if scheduler.get_job('dify_task_initial'):
                scheduler.remove_job('dify_task_initial')
            
            # 立即执行第一次任务（稍微延迟一点确保数据库事务完成）
            scheduler.add_job(
                func=TaskService.execute_task,
                trigger='date',
                run_date=datetime.now() + timedelta(seconds=1),
                id='dify_task_initial',
                replace_existing=True
            )
            
            # 然后按间隔重复执行
            scheduler.add_job(
                func=TaskService.execute_task,
                trigger='interval',
                minutes=interval_minutes,
                start_date=datetime.now() + timedelta(minutes=interval_minutes),
                id='dify_task',
                replace_existing=True
            )
            logger.info(f"任务已调度，1秒后执行第一次，然后每 {interval_minutes} 分钟执行一次")
            
        except Exception as e:
            logger.error(f"任务调度失败: {str(e)}")
            import traceback
            logger.error(f"调度失败详细错误: {traceback.format_exc()}")
    
    @staticmethod
    def stop_task():
        """停止任务"""
        try:
            if scheduler.get_job('dify_task'):
                scheduler.remove_job('dify_task')
                logger.info("重复任务已停止")
            if scheduler.get_job('dify_task_initial'):
                scheduler.remove_job('dify_task_initial')
                logger.info("一次性任务已停止")
            logger.info("所有任务已停止")
        except Exception as e:
            logger.error(f"停止任务失败: {str(e)}")
    
    @staticmethod
    def get_task_logs(page=1, per_page=None):
        """获取任务日志"""
        if per_page is None:
            per_page = Config.LOGS_PER_PAGE_DEFAULT
        
        # 限制最大分页大小
        per_page = min(per_page, Config.LOGS_PER_PAGE_MAX)
        
        from app.models import TaskLog
        return TaskLog.query.order_by(TaskLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_or_create_config():
        """获取或创建配置"""
        from app.models import TaskConfig
        config = TaskConfig.query.first()
        if not config:
            config = TaskConfig()
            db.session.add(config)
            db.session.commit()
        return config 