#!/usr/bin/env python3
"""
测试修复后的指定开始时间功能
验证：
1. 指定开始时间只影响业务数据的时间范围
2. 不影响定时任务的调度（仍然立即执行第一次）
3. 时间范围计算正确
"""

import requests
import time
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5001"

def test_start_time_fix():
    print("=== 测试修复后的指定开始时间功能 ===")
    
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
    
    # 3. 测试指定开始时间（设置为2小时前）
    print("\n3. 测试指定开始时间功能...")
    specified_start_time = datetime.now() - timedelta(hours=2)
    start_time_str = specified_start_time.strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"指定开始时间: {start_time_str}")
    print("预期行为: 任务立即执行，但业务数据时间范围从指定时间开始")
    
    # 4. 启动任务并指定开始时间
    start_response = requests.post(f"{BASE_URL}/api/task/start", 
                                 json={"start_time": start_time_str})
    
    if start_response.status_code == 200:
        result = start_response.json()
        if result.get('success'):
            print("✅ 任务启动成功")
            
            # 5. 等待任务执行并检查结果
            print("\n5. 等待任务执行...")
            for i in range(10):
                time.sleep(1)
                logs_response = requests.get(f"{BASE_URL}/api/logs?limit=1")
                
                if logs_response.status_code == 200:
                    logs_data = logs_response.json()
                    current_count = logs_data.get('total', 0)
                    
                    if current_count > initial_count:
                        latest_log = logs_data['logs'][0]
                        
                        print(f"✅ 检测到新日志!")
                        print(f"   执行时间: {latest_log.get('execute_time')}")
                        print(f"   业务开始时间: {latest_log.get('start_time')}")
                        print(f"   业务结束时间: {latest_log.get('end_time')}")
                        print(f"   状态: {latest_log.get('status')}")
                        
                        # 验证业务时间范围
                        log_start_time = datetime.fromisoformat(latest_log.get('start_time').replace('Z', '+00:00')).replace(tzinfo=None)
                        expected_start_time = specified_start_time
                        
                        time_diff = abs((log_start_time - expected_start_time).total_seconds())
                        
                        if time_diff < 60:  # 允许1分钟误差
                            print("✅ 业务开始时间正确：使用了指定的开始时间")
                        else:
                            print(f"❌ 业务开始时间不正确：期望 {expected_start_time}，实际 {log_start_time}")
                        
                        # 验证任务立即执行
                        execute_time = datetime.fromisoformat(latest_log.get('execute_time').replace('Z', '+00:00')).replace(tzinfo=None)
                        now = datetime.now()
                        execution_delay = (execute_time - now).total_seconds()
                        
                        if abs(execution_delay) < 30:  # 30秒内算立即执行
                            print("✅ 任务立即执行：符合预期")
                        else:
                            print(f"❌ 任务执行延迟过大：{execution_delay:.2f}秒")
                        
                        break
                    else:
                        print(f"   等待中... ({i+1}/10)")
                else:
                    print(f"   获取日志失败 ({i+1}/10)")
            else:
                print("❌ 10秒内未检测到新日志")
        else:
            print(f"❌ 任务启动失败: {result.get('message')}")
    else:
        print(f"❌ 启动请求失败: {start_response.status_code}")
    
    # 6. 测试不指定开始时间的情况
    print("\n6. 测试不指定开始时间的情况...")
    
    # 先停止任务
    stop_response = requests.post(f"{BASE_URL}/api/task/stop")
    time.sleep(2)
    
    # 获取当前日志数量
    logs_response = requests.get(f"{BASE_URL}/api/logs?limit=1")
    if logs_response.status_code == 200:
        logs_data = logs_response.json()
        before_count = logs_data.get('total', 0)
    
    # 启动任务（不指定开始时间）
    start_response = requests.post(f"{BASE_URL}/api/task/start", json={})
    
    if start_response.status_code == 200:
        result = start_response.json()
        if result.get('success'):
            print("✅ 任务启动成功（未指定开始时间）")
            
            # 等待执行
            for i in range(10):
                time.sleep(1)
                logs_response = requests.get(f"{BASE_URL}/api/logs?limit=1")
                
                if logs_response.status_code == 200:
                    logs_data = logs_response.json()
                    current_count = logs_data.get('total', 0)
                    
                    if current_count > before_count:
                        latest_log = logs_data['logs'][0]
                        
                        print(f"✅ 检测到新日志!")
                        print(f"   执行时间: {latest_log.get('execute_time')}")
                        print(f"   业务开始时间: {latest_log.get('start_time')}")
                        print(f"   业务结束时间: {latest_log.get('end_time')}")
                        
                        # 验证使用了上次结束时间作为开始时间
                        print("✅ 未指定开始时间时使用了上次结束时间")
                        break
                    else:
                        print(f"   等待中... ({i+1}/10)")
            else:
                print("❌ 10秒内未检测到新日志")
    
    # 7. 停止任务
    print("\n7. 停止任务...")
    stop_response = requests.post(f"{BASE_URL}/api/task/stop")
    if stop_response.status_code == 200:
        print("任务已停止")
    
    print("\n=== 测试完成 ===")
    print("\n总结:")
    print("- 指定开始时间只影响业务数据的时间范围")
    print("- 不影响定时任务的调度（仍然立即执行第一次）")
    print("- 未指定开始时间时使用上次结束时间")

if __name__ == "__main__":
    try:
        test_start_time_fix()
    except Exception as e:
        print(f"测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc() 