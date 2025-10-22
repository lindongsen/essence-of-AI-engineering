#!/bin/bash

CWD=$(dirname $(readlink -f "$0"))

set -x

cd ${CWD}
[ -d "/林生的奇思妙想/rag" ] && exit 1
cp -r rag /林生的奇思妙想/
cp *.md /林生的奇思妙想/rag/
ls /林生的奇思妙想/rag

cd ${CWD}/../
DEBUG=1 OPENAI_MODEL=DeepSeek-V3.1 uv run AgentReAct.py -p ./rag_abstract/plan-20251018.md -t 发挥你的专业水平完成任务吧


