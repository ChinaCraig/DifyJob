#!/usr/bin/env python3
"""
直接测试execute_task方法
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services import TaskService
from app.models import TaskConfig
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)

def test_execute_task_direct():
    print("=== 直接测试execute_task方法 ===")
    
    # 创建应用实例
    app = create_app()
    TaskService.set_app(app)
    
    with app.app_context():
        # 1. 检查配置
        config = TaskService.get_or_create_config()
        print(f"配置状态: is_active={config.is_active}")
        
        # 2. 如果任务未激活，先激活
        if not config.is_active:
            print("激活任务配置...")
            config.is_active = True
            from app import db
            db.session.commit()
            print(f"配置已激活: is_active={config.is_active}")
        
        # 3. 直接调用execute_task
        print("直接调用execute_task...")
        try:
            TaskService.execute_task()
            print("execute_task调用完成")
        except Exception as e:
            print(f"execute_task调用异常: {e}")
            import traceback
            traceback.print_exc()
        
        # 4. 检查是否产生了新日志
        from app.models import TaskLog
        logs = TaskLog.query.order_by(TaskLog.created_at.desc()).limit(3).all()
        print(f"最近3条日志:")
        for i, log in enumerate(logs):
            print(f"  {i+1}. {log.execute_time} - {log.status}")

if __name__ == "__main__":
    test_execute_task_direct() 