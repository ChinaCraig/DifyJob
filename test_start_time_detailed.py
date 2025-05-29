#!/usr/bin/env python3
"""
详细测试指定开始时间功能
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

def test_start_time_detailed():
    print("=== 详细测试指定开始时间功能 ===")
    
    # 1. 停止任务
    print("\n1. 停止任务...")
    stop_response = requests.post(f"{BASE_URL}/api/task/stop")
    print(f"停止响应: {stop_response.status_code}")
    time.sleep(2)
    
    # 2. 获取当前配置
    print("\n2. 获取当前配置...")
    config_response = requests.get(f"{BASE_URL}/api/config")
    if config_response.status_code == 200:
        config = config_response.json()
        print(f"当前配置:")
        print(f"  - 间隔: {config.get('interval_minutes')} 分钟")
        print(f"  - 是否激活: {config.get('is_active')}")
        print(f"  - 上次结束时间: {config.get('last_end_time')}")
    
    # 3. 获取当前日志数量
    print("\n3. 获取当前日志数量...")
    logs_response = requests.get(f"{BASE_URL}/api/logs?limit=1")
    if logs_response.status_code == 200:
        logs_data = logs_response.json()
        initial_count = logs_data.get('total', 0)
        print(f"当前日志总数: {initial_count}")
        if logs_data.get('logs'):
            latest_log = logs_data['logs'][0]
            print(f"最新日志业务时间: {latest_log.get('start_time')} - {latest_log.get('end_time')}")
    
    # 4. 测试指定开始时间（设置为3小时前）
    print("\n4. 测试指定开始时间功能...")
    specified_start_time = datetime.now() - timedelta(hours=3)
    start_time_str = specified_start_time.strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"指定开始时间: {start_time_str}")
    print("预期行为:")
    print("  - 任务立即执行第一次")
    print("  - 业务数据时间范围从指定时间开始")
    print("  - 下次执行时间从指定时间+间隔开始计算")
    
    # 5. 启动任务并指定开始时间
    print("\n5. 启动任务并指定开始时间...")
    start_response = requests.post(f"{BASE_URL}/api/task/start", 
                                 json={"start_time": start_time_str})
    
    if start_response.status_code == 200:
        result = start_response.json()
        if result.get('success'):
            print("✅ 任务启动成功")
            
            # 6. 检查配置是否更新
            print("\n6. 检查配置更新...")
            config_response = requests.get(f"{BASE_URL}/api/config")
            if config_response.status_code == 200:
                updated_config = config_response.json()
                print(f"更新后的配置:")
                print(f"  - 是否激活: {updated_config.get('is_active')}")
                print(f"  - 上次结束时间: {updated_config.get('last_end_time')}")
                
                # 验证last_end_time是否设置为指定时间
                if updated_config.get('last_end_time') == start_time_str:
                    print("✅ 配置中的last_end_time正确设置为指定开始时间")
                else:
                    print(f"❌ 配置中的last_end_time不正确: 期望 {start_time_str}, 实际 {updated_config.get('last_end_time')}")
            
            # 7. 等待任务执行并检查结果
            print("\n7. 等待任务执行...")
            for i in range(15):
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
                        log_start_time_str = latest_log.get('start_time')
                        log_end_time_str = latest_log.get('end_time')
                        
                        # 解析时间字符串
                        try:
                            if 'T' in log_start_time_str:
                                log_start_time = datetime.fromisoformat(log_start_time_str.replace('Z', '+00:00')).replace(tzinfo=None)
                            else:
                                log_start_time = datetime.strptime(log_start_time_str, '%Y-%m-%d %H:%M:%S')
                            
                            if 'T' in log_end_time_str:
                                log_end_time = datetime.fromisoformat(log_end_time_str.replace('Z', '+00:00')).replace(tzinfo=None)
                            else:
                                log_end_time = datetime.strptime(log_end_time_str, '%Y-%m-%d %H:%M:%S')
                            
                            expected_start_time = specified_start_time
                            expected_end_time = specified_start_time + timedelta(minutes=updated_config.get('interval_minutes', 1))
                            
                            start_time_diff = abs((log_start_time - expected_start_time).total_seconds())
                            end_time_diff = abs((log_end_time - expected_end_time).total_seconds())
                            
                            if start_time_diff < 60:  # 允许1分钟误差
                                print("✅ 业务开始时间正确：使用了指定的开始时间")
                            else:
                                print(f"❌ 业务开始时间不正确：期望 {expected_start_time}，实际 {log_start_time}")
                            
                            if end_time_diff < 60:  # 允许1分钟误差
                                print("✅ 业务结束时间正确：基于指定开始时间+间隔计算")
                            else:
                                print(f"❌ 业务结束时间不正确：期望 {expected_end_time}，实际 {log_end_time}")
                            
                        except Exception as e:
                            print(f"❌ 时间解析错误: {e}")
                        
                        # 验证任务立即执行
                        execute_time_str = latest_log.get('execute_time')
                        try:
                            if 'T' in execute_time_str:
                                execute_time = datetime.fromisoformat(execute_time_str.replace('Z', '+00:00')).replace(tzinfo=None)
                            else:
                                execute_time = datetime.strptime(execute_time_str, '%Y-%m-%d %H:%M:%S')
                            
                            now = datetime.now()
                            execution_delay = abs((execute_time - now).total_seconds())
                            
                            if execution_delay < 60:  # 60秒内算立即执行
                                print("✅ 任务立即执行：符合预期")
                            else:
                                print(f"❌ 任务执行延迟过大：{execution_delay:.2f}秒")
                        except Exception as e:
                            print(f"❌ 执行时间解析错误: {e}")
                        
                        break
                    else:
                        print(f"   等待中... ({i+1}/15)")
                else:
                    print(f"   获取日志失败 ({i+1}/15)")
            else:
                print("❌ 15秒内未检测到新日志")
        else:
            print(f"❌ 任务启动失败: {result.get('message')}")
    else:
        print(f"❌ 启动请求失败: {start_response.status_code}")
    
    # 8. 检查配置的最终状态
    print("\n8. 检查配置的最终状态...")
    config_response = requests.get(f"{BASE_URL}/api/config")
    if config_response.status_code == 200:
        final_config = config_response.json()
        print(f"最终配置:")
        print(f"  - 是否激活: {final_config.get('is_active')}")
        print(f"  - 上次结束时间: {final_config.get('last_end_time')}")
        
        # 验证last_end_time是否已更新为新的结束时间
        expected_new_end_time = specified_start_time + timedelta(minutes=final_config.get('interval_minutes', 1))
        final_last_end_time_str = final_config.get('last_end_time')
        
        try:
            final_last_end_time = datetime.strptime(final_last_end_time_str, '%Y-%m-%d %H:%M:%S')
            time_diff = abs((final_last_end_time - expected_new_end_time).total_seconds())
            
            if time_diff < 60:
                print("✅ 配置的last_end_time已正确更新为新的结束时间")
            else:
                print(f"❌ 配置的last_end_time更新不正确：期望 {expected_new_end_time}，实际 {final_last_end_time}")
        except Exception as e:
            print(f"❌ 最终时间解析错误: {e}")
    
    # 9. 停止任务
    print("\n9. 停止任务...")
    stop_response = requests.post(f"{BASE_URL}/api/task/stop")
    if stop_response.status_code == 200:
        print("任务已停止")
    
    print("\n=== 测试完成 ===")
    print("\n总结:")
    print("- 指定开始时间功能测试完成")
    print("- 验证了业务数据时间范围的正确性")
    print("- 验证了任务立即执行的功能")
    print("- 验证了配置更新的正确性")

if __name__ == "__main__":
    try:
        test_start_time_detailed()
    except Exception as e:
        print(f"测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc() 