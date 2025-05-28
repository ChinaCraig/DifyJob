#!/bin/bash

echo "Dify任务调度系统启动脚本"
echo "========================"

# 检查Python版本
python_version=$(python3 --version 2>&1)
echo "Python版本: $python_version"

# 检查是否安装了依赖
echo "检查依赖..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "正在安装依赖..."
    pip3 install -r requirements.txt
fi

# 从配置文件读取端口号
if [ -f "config.env" ]; then
    FLASK_PORT=$(grep "^FLASK_PORT=" config.env | cut -d'=' -f2)
    FLASK_HOST=$(grep "^FLASK_HOST=" config.env | cut -d'=' -f2)
else
    FLASK_PORT=5001
    FLASK_HOST=0.0.0.0
fi

# 设置环境变量
export FLASK_APP=run.py
export FLASK_ENV=development

echo "启动应用..."
echo "访问地址: http://${FLASK_HOST}:${FLASK_PORT}"
echo "按 Ctrl+C 停止应用"
echo "========================"

python3 run.py 