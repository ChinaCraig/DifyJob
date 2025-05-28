from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, timedelta
from app import db
from app.models import TaskLog, TaskConfig
from app.services import TaskService
from app.config import Config

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """主页"""
    config = TaskService.get_or_create_config()
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = Config.LOGS_PER_PAGE_DEFAULT  # 使用配置文件中的默认值
    
    # 获取最近的日志
    logs_pagination = TaskService.get_task_logs(page=page, per_page=per_page)
    logs = logs_pagination.items
    
    return render_template('index.html', config=config, logs=logs, logs_pagination=logs_pagination)

@main.route('/logs')
def logs():
    """日志页面"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', Config.LOGS_PER_PAGE_DEFAULT * 2, type=int)  # 日志页面默认显示更多
    logs_pagination = TaskService.get_task_logs(page=page, per_page=per_page)
    
    return render_template('logs.html', logs_pagination=logs_pagination)

@main.route('/debug-config')
def debug_config():
    """配置变更检测调试页面"""
    return render_template('debug_config.html')

@main.route('/api/config', methods=['GET'])
def get_config():
    """获取配置"""
    config = TaskService.get_or_create_config()
    return jsonify(config.to_dict())

@main.route('/api/config', methods=['POST'])
def update_config():
    """更新配置"""
    try:
        data = request.get_json()
        config = TaskService.get_or_create_config()
        
        # 更新配置
        old_interval = config.interval_minutes
        if 'interval_minutes' in data:
            config.interval_minutes = int(data['interval_minutes'])
        if 'dify_api_key' in data:
            config.dify_api_key = data['dify_api_key']
        if 'dify_url' in data:
            config.dify_url = data['dify_url']
        
        config.updated_at = datetime.now()
        db.session.commit()
        
        # 如果任务正在运行且间隔时间发生变化，重新调度任务
        if config.is_active and 'interval_minutes' in data and old_interval != config.interval_minutes:
            TaskService.schedule_task(config.interval_minutes)
        
        return jsonify({'success': True, 'message': '配置更新成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/api/task/start', methods=['POST'])
def start_task():
    """启动任务"""
    try:
        data = request.get_json()
        config = TaskService.get_or_create_config()
        
        # 设置开始时间
        start_time = None
        if 'start_time' in data and data['start_time']:
            start_time = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S')
            config.last_end_time = start_time
        elif not config.last_end_time:
            # 如果没有指定开始时间且没有历史结束时间，使用当前时间
            config.last_end_time = datetime.now()
        
        # 启用任务
        config.is_active = True
        config.updated_at = datetime.now()
        db.session.commit()
        
        # 调度任务，传递开始时间
        TaskService.schedule_task(config.interval_minutes, start_time)
        
        return jsonify({'success': True, 'message': '任务启动成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/api/task/stop', methods=['POST'])
def stop_task():
    """停止任务"""
    try:
        config = TaskService.get_or_create_config()
        config.is_active = False
        config.updated_at = datetime.now()
        db.session.commit()
        
        # 停止调度
        TaskService.stop_task()
        
        return jsonify({'success': True, 'message': '任务停止成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/api/task/execute', methods=['POST'])
def execute_task_now():
    """立即执行任务"""
    try:
        TaskService.execute_task()
        return jsonify({'success': True, 'message': '任务执行完成'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/api/logs')
def get_logs():
    """获取日志API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', Config.LOGS_PER_PAGE_DEFAULT, type=int)
    limit = request.args.get('limit', type=int)  # 新增limit参数
    
    # 如果指定了limit，则使用limit而不是分页
    if limit:
        per_page = min(limit, Config.LOGS_PER_PAGE_MAX)  # 限制最大值
        page = 1
    
    logs_pagination = TaskService.get_task_logs(page=page, per_page=per_page)
    
    return jsonify({
        'logs': [log.to_dict() for log in logs_pagination.items],
        'total': logs_pagination.total,
        'pages': logs_pagination.pages,
        'current_page': logs_pagination.page,
        'per_page': per_page,
        'has_next': logs_pagination.has_next,
        'has_prev': logs_pagination.has_prev
    })

@main.route('/api/app-config')
def get_app_config():
    """获取应用配置（供前端使用）"""
    return jsonify({
        'auto_refresh_interval_seconds': Config.AUTO_REFRESH_INTERVAL_SECONDS,
        'near_execution_refresh_seconds': Config.NEAR_EXECUTION_REFRESH_SECONDS,
        'logs_per_page_default': Config.LOGS_PER_PAGE_DEFAULT,
        'logs_per_page_max': Config.LOGS_PER_PAGE_MAX
    }) 