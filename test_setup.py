#!/usr/bin/env python3
"""
项目配置测试脚本
用于验证项目的基本配置是否正确
"""

import sys
import os

def test_imports():
    """测试必要的包导入"""
    print("测试包导入...")
    
    try:
        import flask
        print("✅ Flask 导入成功")
    except ImportError as e:
        print(f"❌ Flask 导入失败: {e}")
        return False
    
    try:
        import pymysql
        print("✅ PyMySQL 导入成功")
    except ImportError as e:
        print(f"❌ PyMySQL 导入失败: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests 导入成功")
    except ImportError as e:
        print(f"❌ Requests 导入失败: {e}")
        return False
    
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        print("✅ APScheduler 导入成功")
    except ImportError as e:
        print(f"❌ APScheduler 导入失败: {e}")
        return False
    
    return True

def test_project_structure():
    """测试项目结构"""
    print("\n测试项目结构...")
    
    required_files = [
        'app/__init__.py',
        'app/models.py',
        'app/routes.py',
        'app/services.py',
        'app/templates/base.html',
        'app/templates/index.html',
        'app/templates/logs.html',
        'database/create_tables.sql',
        'requirements.txt',
        'run.py',
        'README.md'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} 不存在")
            all_exist = False
    
    return all_exist

def test_app_creation():
    """测试Flask应用创建和数据库连接"""
    print("\n测试Flask应用创建和数据库连接...")
    
    try:
        # 添加当前目录到Python路径
        sys.path.insert(0, os.getcwd())
        
        # 测试基本导入
        from app import db, scheduler, create_app
        print("✅ 应用模块导入成功")
        
        from app.models import TaskLog, TaskConfig
        print("✅ 数据模型导入成功")
        
        from app.services import TaskService
        print("✅ 服务模块导入成功")
        
        from app.routes import main
        print("✅ 路由模块导入成功")
        
        # 测试Flask应用创建
        app = create_app()
        print("✅ Flask应用创建成功")
        print(f"✅ 应用名称: {app.name}")
        
        # 测试数据库连接
        with app.app_context():
            # 测试数据库连接
            from sqlalchemy import text
            with db.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                print("✅ 数据库连接成功")
                
                # 测试表是否存在
                result = connection.execute(text("SHOW TABLES LIKE 'task_configs'"))
                if result.fetchone():
                    print("✅ task_configs表存在")
                else:
                    print("⚠️  task_configs表不存在")
                
                result = connection.execute(text("SHOW TABLES LIKE 'task_logs'"))
                if result.fetchone():
                    print("✅ task_logs表存在")
                else:
                    print("⚠️  task_logs表不存在")
            
            # 测试配置服务
            config = TaskService.get_or_create_config()
            print(f"✅ 配置服务正常，当前间隔: {config.interval_minutes}分钟")
        
        # 测试路由
        with app.test_client() as client:
            print("✅ 测试客户端创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 应用测试失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("Dify任务调度系统 - 配置测试")
    print("=" * 50)
    
    tests = [
        ("包导入测试", test_imports),
        ("项目结构测试", test_project_structure),
        ("应用和数据库测试", test_app_creation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！项目配置正确。")
        print("\n下一步:")
        print("1. 确保MySQL数据库运行正常")
        print("2. 执行数据库建表语句: database/create_tables.sql")
        print("3. 配置config.env中的Dify API Key")
        print("4. 运行: python run.py 或 ./start.sh")
    else:
        print("❌ 部分测试失败，请检查项目配置。")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 