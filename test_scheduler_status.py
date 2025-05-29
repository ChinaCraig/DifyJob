#!/usr/bin/env python3
"""
检查调度器状态
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, scheduler
from app.services import TaskService
import logging
import time

# 设置日志级别
logging.basicConfig(level=logging.INFO)

def check_scheduler_status():
    print("=== 检查调度器状态 ===")
    
    # 创建应用实例
    app = create_app()
    TaskService.set_app(app)
    
    with app.app_context():
        print(f"调度器运行状态: {scheduler.running}")
        print(f"调度器状态: {scheduler.state}")
        
        # 启动调度器
        if not scheduler.running:
            scheduler.start()
            print("调度器已启动")
        
        # 获取所有任务
        jobs = scheduler.get_jobs()
        print(f"当前任务数量: {len(jobs)}")
        
        for job in jobs:
            print(f"任务ID: {job.id}")
            print(f"任务函数: {job.func}")
            try:
                print(f"下次执行时间: {job.next_run_time}")
            except:
                print("下次执行时间: 无法获取")
            print(f"触发器: {job.trigger}")
            print("---")
        
        # 测试启动任务
        print("\n测试启动任务...")
        config = TaskService.get_or_create_config()
        config.is_active = True
        from app import db
        db.session.commit()
        
        TaskService.schedule_task(config.interval_minutes)
        
        # 再次检查任务
        jobs = scheduler.get_jobs()
        print(f"启动后任务数量: {len(jobs)}")
        
        for job in jobs:
            print(f"任务ID: {job.id}")
            print(f"任务函数: {job.func}")
            try:
                print(f"下次执行时间: {job.next_run_time}")
            except:
                print("下次执行时间: 无法获取")
            print("---")
        
        # 等待一下看任务是否执行
        print("\n等待3秒看任务是否执行...")
        time.sleep(3)
        
        # 检查日志
        from app.models import TaskLog
        logs = TaskLog.query.order_by(TaskLog.created_at.desc()).limit(1).all()
        if logs:
            latest_log = logs[0]
            print(f"最新日志: {latest_log.execute_time} - {latest_log.status}")
        else:
            print("没有日志记录")

if __name__ == "__main__":
    check_scheduler_status() 