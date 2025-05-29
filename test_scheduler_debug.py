#!/usr/bin/env python3
"""
测试调度器是否正常工作
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5001"

def test_scheduler():
    print("=== 测试调度器功能 ===")
    
    # 1. 停止任务
    print("\n1. 停止任务...")
    stop_response = requests.post(f"{BASE_URL}/api/task/stop")
    print(f"停止响应: {stop_response.status_code}")
    time.sleep(2)
    
    # 2. 获取当前日志数量
    print("\n2. 获取当前日志数量...")
    logs_response = requests.get(f"{BASE_URL}/api/logs?limit=1")
    if logs_response.status_code == 200:
        logs_data = logs_response.json()
        initial_count = logs_data.get('total', 0)
        print(f"当前日志总数: {initial_count}")
    
    # 3. 测试立即执行功能
    print("\n3. 测试立即执行功能...")
    execute_response = requests.post(f"{BASE_URL}/api/task/execute")
    print(f"立即执行响应: {execute_response.status_code}")
    if execute_response.status_code == 200:
        result = execute_response.json()
        print(f"立即执行结果: {result}")
        
        # 检查是否产生新日志
        time.sleep(2)
        logs_response = requests.get(f"{BASE_URL}/api/logs?limit=1")
        if logs_response.status_code == 200:
            logs_data = logs_response.json()
            new_count = logs_data.get('total', 0)
            print(f"执行后日志总数: {new_count}")
            if new_count > initial_count:
                print("✅ 立即执行功能正常")
            else:
                print("❌ 立即执行功能异常")
    
    # 4. 测试启动任务
    print("\n4. 测试启动任务...")
    start_response = requests.post(f"{BASE_URL}/api/task/start", json={})
    print(f"启动响应: {start_response.status_code}")
    if start_response.status_code == 200:
        result = start_response.json()
        print(f"启动结果: {result}")
        
        # 等待5秒检查是否有新日志
        print("等待5秒检查调度器执行...")
        time.sleep(5)
        
        logs_response = requests.get(f"{BASE_URL}/api/logs?limit=1")
        if logs_response.status_code == 200:
            logs_data = logs_response.json()
            final_count = logs_data.get('total', 0)
            print(f"最终日志总数: {final_count}")
            if final_count > new_count:
                print("✅ 调度器立即执行功能正常")
            else:
                print("❌ 调度器立即执行功能异常")
    
    # 5. 停止任务
    print("\n5. 停止任务...")
    stop_response = requests.post(f"{BASE_URL}/api/task/stop")
    print(f"停止响应: {stop_response.status_code}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    try:
        test_scheduler()
    except Exception as e:
        print(f"测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc() 