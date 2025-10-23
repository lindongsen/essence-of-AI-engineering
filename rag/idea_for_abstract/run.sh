#!/bin/bash
set -e

CPATH=$(readlink -f "$0")
CWD=$(dirname "${CPATH}")

set -x

cd "${CWD}"

WORKSPACE="/林生的奇思妙想/rag"

[ -d "${WORKSPACE}" ] && exit 1
cp -r rag /林生的奇思妙想/
cp *.md "${WORKSPACE}"
ls "${WORKSPACE}"

cd "${CWD}/../../"
DEBUG=1 OPENAI_MODEL=DeepSeek-V3.1 uv run AgentReAct.py -p ./rag/idea_for_abstract/plan-20251018.md -t 发挥你的专业水平完成任务吧
