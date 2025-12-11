#!/bin/bash

# RAG Server启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 设置Python路径
export PYTHONPATH="/林生的奇思妙想/TopsailAI:$PYTHONPATH"

# 检查服务是否已经在运行
if pgrep -f "rag_server.py" > /dev/null; then
    echo "RAG Server is already running"
    exit 1
fi

# 启动服务
echo "Starting RAG Server..."
nohup uv run python rag_server.py >> rag_server.log 2>&1 &

# 等待服务启动
sleep 3

# 检查服务是否启动成功
if pgrep -f "rag_server.py" > /dev/null; then
    echo "RAG Server started successfully"
    echo "PID: $(pgrep -f 'rag_server.py')"
    echo "Log file: $SCRIPT_DIR/rag_server.log"
else
    echo "Failed to start RAG Server"
    echo "Check log file: $SCRIPT_DIR/rag_server.log"
    exit 1
fi