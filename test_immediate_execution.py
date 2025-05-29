#!/usr/bin/env python3
"""
专门测试启动任务时立即执行功能
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5001"

def test_immediate_execution():
    print("=== 测试启动任务立即执行功能 ===")
    
    # 1. 确保任务已停止
    print("\n1. 确保任务已停止...")
    stop_response = requests.post(f"{BASE_URL}/api/task/stop")
    print(f"停止任务响应: {stop_response.status_code}")
    time.sleep(2)
    
    # 2. 获取启动前的日志
    print("\n2. 获取启动前的日志...")
    logs_response = requests.get(f"{BASE_URL}/api/logs?limit=3")
    if logs_response.status_code == 200:
        logs_data = logs_response.json()
        initial_count = logs_data.get('total', 0)
        print(f"启动前日志总数: {initial_count}")
        
        if logs_data.get('logs'):
            for i, log in enumerate(logs_data['logs'][:3]):
                print(f"  日志{i+1}: {log.get('execute_time')} - {log.get('status')}")
    
    # 3. 启动任务
    print("\n3. 启动任务...")
    start_time = datetime.now()
    
    try:
        start_response = requests.post(f"{BASE_URL}/api/task/start", json={})
        print(f"启动响应状态码: {start_response.status_code}")
        print(f"启动响应内容: {start_response.text}")
        
        if start_response.status_code == 200:
            result = start_response.json()
            print(f"启动响应JSON: {result}")
            
            if result.get('success'):
                print("✅ 任务启动成功")
                
                # 4. 立即检查是否有新日志（多次检查）
                print("\n4. 检查立即执行结果...")
                for i in range(15):  # 检查15秒
                    time.sleep(1)
                    logs_response = requests.get(f"{BASE_URL}/api/logs?limit=1")
                    
                    if logs_response.status_code == 200:
                        logs_data = logs_response.json()
                        current_count = logs_data.get('total', 0)
                        
                        if current_count > initial_count:
                            latest_log = logs_data['logs'][0]
                            try:
                                execute_time = datetime.fromisoformat(latest_log.get('execute_time').replace('Z', '+00:00'))
                                time_diff = (execute_time.replace(tzinfo=None) - start_time).total_seconds()
                            except:
                                time_diff = 0
                            
                            print(f"✅ 检测到新日志!")
                            print(f"   执行时间: {latest_log.get('execute_time')}")
                            print(f"   启动后延迟: {time_diff:.2f}秒")
                            print(f"   状态: {latest_log.get('status')}")
                            print(f"   时间范围: {latest_log.get('start_time')} -> {latest_log.get('end_time')}")
                            break
                        else:
                            print(f"   等待中... ({i+1}/15) - 当前日志数: {current_count}")
                    else:
                        print(f"   获取日志失败 ({i+1}/15)")
                else:
                    print("❌ 15秒内未检测到新日志")
            else:
                print(f"❌ 任务启动失败: {result.get('message')}")
        else:
            print(f"❌ 启动请求失败: {start_response.status_code}")
            print(f"错误内容: {start_response.text}")
    except Exception as e:
        print(f"❌ 启动请求异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. 再次停止任务
    print("\n5. 停止任务...")
    stop_response = requests.post(f"{BASE_URL}/api/task/stop")
    if stop_response.status_code == 200:
        print("任务已停止")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    try:
        test_immediate_execution()
    except Exception as e:
        print(f"测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc() 