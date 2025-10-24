#!/bin/bash

# RAG Server停止脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查服务是否在运行
if ! pgrep -f "rag_server.py" > /dev/null; then
    echo "RAG Server is not running"
    exit 0
fi

# 获取PID
PID=$(pgrep -f "rag_server.py")
echo "Stopping RAG Server (PID: $PID)..."

# 发送关闭信号
kill $PID

# 等待进程结束
for i in {1..10}; do
    if ! pgrep -f "rag_server.py" > /dev/null; then
        echo "RAG Server stopped successfully"
        exit 0
    fi
    sleep 1
done

# 如果进程还在运行，强制杀死
if pgrep -f "rag_server.py" > /dev/null; then
    echo "Force killing RAG Server..."
    kill -9 $PID
    sleep 1
    
    if ! pgrep -f "rag_server.py" > /dev/null; then
        echo "RAG Server force stopped"
    else
        echo "Failed to stop RAG Server"
        exit 1
    fi
fi