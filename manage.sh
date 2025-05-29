#!/bin/bash

PID_FILE="gunicorn.pid"

start() {
    echo "Starting Gunicorn..."
    ./start_prod.sh
    echo "Gunicorn started"
}

stop() {
    echo "Stopping Gunicorn..."
    if [ -f $PID_FILE ]; then
        pid=$(cat $PID_FILE)
        kill $pid
        rm $PID_FILE
        echo "Gunicorn stopped"
    else
        echo "PID file not found"
        # 尝试查找并杀死所有 gunicorn 进程
        pkill -f gunicorn
    fi
}

status() {
    if [ -f $PID_FILE ]; then
        pid=$(cat $PID_FILE)
        if ps -p $pid > /dev/null; then
            echo "Gunicorn is running (PID: $pid)"
        else
            echo "PID file exists but Gunicorn is not running"
            rm $PID_FILE
        fi
    else
        echo "Gunicorn is not running"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 2
        start
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0 