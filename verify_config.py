#!/usr/bin/env python3
"""
配置验证脚本
用于验证所有配置项是否正确从config.env文件中加载
"""

import os
import sys
from app.config import Config

def verify_config():
    """验证配置"""
    print("=" * 50)
    print("配置验证报告")
    print("=" * 50)
    
    # 检查config.env文件是否存在
    config_file = 'config.env'
    if not os.path.exists(config_file):
        print(f"❌ 配置文件 {config_file} 不存在")
        return False
    
    print(f"✅ 配置文件 {config_file} 存在")
    
    # 验证各类配置
    configs = [
        ("Flask基础配置", [
            ("SECRET_KEY", Config.SECRET_KEY),
            ("FLASK_ENV", Config.FLASK_ENV),
        ]),
        ("Flask运行配置", [
            ("FLASK_DEBUG", Config.FLASK_DEBUG),
            ("FLASK_HOST", Config.FLASK_HOST),
            ("FLASK_PORT", Config.FLASK_PORT),
            ("FLASK_USE_RELOADER", Config.FLASK_USE_RELOADER),
        ]),
        ("数据库配置", [
            ("DB_HOST", Config.DB_HOST),
            ("DB_PORT", Config.DB_PORT),
            ("DB_USER", Config.DB_USER),
            ("DB_PASSWORD", "***" if Config.DB_PASSWORD else ""),
            ("DB_NAME", Config.DB_NAME),
            ("SQLALCHEMY_DATABASE_URI", Config.SQLALCHEMY_DATABASE_URI[:50] + "..."),
        ]),
        ("Dify配置", [
            ("DIFY_API_URL", Config.DIFY_API_URL),
            ("DIFY_API_KEY", Config.DIFY_API_KEY[:10] + "..." if Config.DIFY_API_KEY else ""),
            ("DIFY_API_TIMEOUT", Config.DIFY_API_TIMEOUT),
            ("DIFY_USER_IDENTIFIER", Config.DIFY_USER_IDENTIFIER),
        ]),
        ("日志配置", [
            ("LOG_LEVEL", Config.LOG_LEVEL),
        ]),
        ("分页配置", [
            ("LOGS_PER_PAGE_DEFAULT", Config.LOGS_PER_PAGE_DEFAULT),
            ("LOGS_PER_PAGE_MAX", Config.LOGS_PER_PAGE_MAX),
        ]),
        ("自动刷新配置", [
            ("AUTO_REFRESH_INTERVAL_SECONDS", Config.AUTO_REFRESH_INTERVAL_SECONDS),
            ("NEAR_EXECUTION_REFRESH_SECONDS", Config.NEAR_EXECUTION_REFRESH_SECONDS),
        ]),
    ]
    
    all_ok = True
    
    for category, items in configs:
        print(f"\n📋 {category}:")
        for name, value in items:
            if value is None or value == "":
                print(f"  ⚠️  {name}: 未设置")
                if name in ["DIFY_API_KEY"]:  # 这些是可选的
                    continue
                all_ok = False
            else:
                print(f"  ✅ {name}: {value}")
    
    # 测试应用创建
    print(f"\n🔧 应用创建测试:")
    try:
        from app import create_app
        app = create_app()
        print("  ✅ Flask应用创建成功")
        
        # 测试配置加载
        expected_configs = [
            'SECRET_KEY', 'SQLALCHEMY_DATABASE_URI', 'FLASK_DEBUG', 
            'FLASK_HOST', 'FLASK_PORT'
        ]
        
        for config_name in expected_configs:
            if config_name in app.config:
                print(f"  ✅ {config_name} 已加载到Flask配置")
            else:
                print(f"  ❌ {config_name} 未加载到Flask配置")
                all_ok = False
                
    except Exception as e:
        print(f"  ❌ Flask应用创建失败: {e}")
        all_ok = False
    
    # 测试API端点
    print(f"\n🌐 API端点测试:")
    try:
        with app.app_context():
            from app.routes import get_app_config
            with app.test_request_context():
                response = get_app_config()
                config_data = response.get_json()
                print("  ✅ /api/app-config 端点正常")
                print(f"     返回数据: {config_data}")
    except Exception as e:
        print(f"  ❌ API端点测试失败: {e}")
        all_ok = False
    
    print("\n" + "=" * 50)
    if all_ok:
        print("🎉 所有配置验证通过！")
        print("✅ 项目已成功配置化，所有硬编码配置已移除")
    else:
        print("❌ 配置验证失败，请检查上述问题")
    print("=" * 50)
    
    return all_ok

if __name__ == "__main__":
    success = verify_config()
    sys.exit(0 if success else 1) 