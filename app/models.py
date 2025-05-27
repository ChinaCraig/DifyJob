from app import db
from datetime import datetime

class TaskLog(db.Model):
    """任务执行日志表"""
    __tablename__ = 'task_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    interval_minutes = db.Column(db.Integer, nullable=False, comment='间隔时间(分钟)')
    execute_time = db.Column(db.DateTime, nullable=False, comment='执行时间')
    start_time = db.Column(db.DateTime, nullable=False, comment='起始时间')
    end_time = db.Column(db.DateTime, nullable=False, comment='结束时间')
    status = db.Column(db.String(20), default='success', comment='执行状态')
    response_data = db.Column(db.Text, comment='响应数据')
    error_message = db.Column(db.Text, comment='错误信息')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'interval_minutes': self.interval_minutes,
            'execute_time': self.execute_time.strftime('%Y-%m-%d %H:%M:%S'),
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status,
            'response_data': self.response_data,
            'error_message': self.error_message,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class TaskConfig(db.Model):
    """任务配置表"""
    __tablename__ = 'task_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    interval_minutes = db.Column(db.Integer, default=30, comment='间隔时间(分钟)')
    is_active = db.Column(db.Boolean, default=False, comment='是否启用')
    last_end_time = db.Column(db.DateTime, comment='最后结束时间')
    dify_api_key = db.Column(db.String(255), comment='Dify API Key')
    dify_url = db.Column(db.String(500), default='http://localhost/v1/workflows/run', comment='Dify API URL')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'interval_minutes': self.interval_minutes,
            'is_active': self.is_active,
            'last_end_time': self.last_end_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_end_time else None,
            'dify_api_key': self.dify_api_key,
            'dify_url': self.dify_url,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        } 