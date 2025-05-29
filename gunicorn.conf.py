# Gunicorn 配置文件
import multiprocessing
import os

# 创建日志目录
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 绑定的地址和端口
bind = "0.0.0.0:5002"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = "sync"

# 超时时间
timeout = 120

# 日志配置
accesslog = os.path.join(log_dir, "gunicorn_access.log")
errorlog = os.path.join(log_dir, "gunicorn_error.log")
loglevel = "info"  # 可选: debug, info, warning, error, critical

# 访问日志格式
access_log_format = '%({x-real-ip}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 后台运行
daemon = True

# PID文件
pidfile = "gunicorn.pid"

# 重载
reload = False 