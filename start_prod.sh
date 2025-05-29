#!/bin/bash

# 激活虚拟环境（如果有的话）
source venv/bin/activate

# 使用 Gunicorn 启动应用
gunicorn -c gunicorn.conf.py run:app 