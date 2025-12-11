#!/bin/bash
set -e

CPATH=$(readlink -f "$0")
CWD=$(dirname "${CPATH}")

set -x

WORKSPACE="/林生的奇思妙想/rag"

[ -d "/林生的奇思妙想/TopsailAI" ] || exit 1
[ -d "${WORKSPACE}" ] && exit 2

cd "${CWD}"
cp -r rag /林生的奇思妙想/
cp *.md "${WORKSPACE}"
ls "${WORKSPACE}"

cd "${CWD}/../../"
DEBUG=1 uv run AgentReAct.py -p ./rag/idea_for_abstract/plan-20251018.md -t 发挥你的专业水平完成任务吧
