#!/usr/bin/env python3
"""
测试任务改进功能
1. 验证启动任务时立即执行第一次
2. 验证日志刷新功能
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5001"

def test_task_improvements():
    print("=== 测试任务改进功能 ===")
    
    # 1. 获取当前配置
    print("\n1. 获取当前配置...")
    config_response = requests.get(f"{BASE_URL}/api/config")
    if config_response.status_code == 200:
        config = config_response.json()
        print(f"当前配置: 间隔={config.get('interval_minutes')}分钟, 状态={'运行中' if config.get('is_active') else '已停止'}")
    else:
        print("获取配置失败")
        return
    
    # 2. 如果任务正在运行，先停止
    if config.get('is_active'):
        print("\n2. 停止当前运行的任务...")
        stop_response = requests.post(f"{BASE_URL}/api/task/stop")
        if stop_response.status_code == 200:
            print("任务停止成功")
            time.sleep(2)
        else:
            print("停止任务失败")
            return
    
    # 3. 获取启动前的日志数量
    print("\n3. 获取启动前的日志数量...")
    logs_response = requests.get(f"{BASE_URL}/api/logs?limit=1")
    if logs_response.status_code == 200:
        logs_data = logs_response.json()
        initial_log_count = logs_data.get('total', 0)
        print(f"启动前日志总数: {initial_log_count}")
        
        if logs_data.get('logs'):
            latest_log = logs_data['logs'][0]
            print(f"最新日志时间: {latest_log.get('execute_time')}")
    else:
        print("获取日志失败")
        return
    
    # 4. 启动任务（应该立即执行第一次）
    print("\n4. 启动任务...")
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    start_response = requests.post(f"{BASE_URL}/api/task/start", 
                                 json={"start_time": start_time})
    if start_response.status_code == 200:
        result = start_response.json()
        if result.get('success'):
            print("任务启动成功")
        else:
            print(f"任务启动失败: {result.get('message')}")
            return
    else:
        print("启动任务请求失败")
        return
    
    # 5. 等待几秒钟，检查是否立即执行了第一次任务
    print("\n5. 等待任务执行...")
    for i in range(10):
        time.sleep(1)
        logs_response = requests.get(f"{BASE_URL}/api/logs?limit=1")
        if logs_response.status_code == 200:
            logs_data = logs_response.json()
            current_log_count = logs_data.get('total', 0)
            
            if current_log_count > initial_log_count:
                latest_log = logs_data['logs'][0]
                print(f"✅ 检测到新日志! 执行时间: {latest_log.get('execute_time')}")
                print(f"   状态: {latest_log.get('status')}")
                print(f"   时间范围: {latest_log.get('start_time')} -> {latest_log.get('end_time')}")
                break
            else:
                print(f"   等待中... ({i+1}/10)")
        else:
            print(f"   获取日志失败 ({i+1}/10)")
    else:
        print("❌ 10秒内未检测到新日志，可能任务未立即执行")
    
    # 6. 测试立即执行功能
    print("\n6. 测试立即执行功能...")
    execute_response = requests.post(f"{BASE_URL}/api/task/execute")
    if execute_response.status_code == 200:
        result = execute_response.json()
        if result.get('success'):
            print("立即执行成功")
            
            # 等待几秒钟检查新日志
            time.sleep(3)
            logs_response = requests.get(f"{BASE_URL}/api/logs?limit=2")
            if logs_response.status_code == 200:
                logs_data = logs_response.json()
                if len(logs_data.get('logs', [])) >= 2:
                    latest_log = logs_data['logs'][0]
                    print(f"✅ 立即执行产生新日志: {latest_log.get('execute_time')}")
                else:
                    print("❌ 立即执行后未检测到新日志")
        else:
            print(f"立即执行失败: {result.get('message')}")
    else:
        print("立即执行请求失败")
    
    # 7. 停止任务
    print("\n7. 停止任务...")
    stop_response = requests.post(f"{BASE_URL}/api/task/stop")
    if stop_response.status_code == 200:
        result = stop_response.json()
        if result.get('success'):
            print("任务停止成功")
        else:
            print(f"任务停止失败: {result.get('message')}")
    else:
        print("停止任务请求失败")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    try:
        test_task_improvements()
    except Exception as e:
        print(f"测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc() 