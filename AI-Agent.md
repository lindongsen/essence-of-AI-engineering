# AgentReAct
一个能执行命令行的AI-Agent，基于ReAct模式运行。


# AgentPlanAndExecute
一个能调用AgentReAct的AI-Agent，基于Plan-And-Execute模式运行。


# 运行方法
1. 设置环境
```
cp env_template .env
编辑 .env 文件
```

2. 运行命令
设置环境变量“DEBUG=1”会打印出每个步骤，不设置就不打印。

举例：
```
~# DEBUG=1 uv run cli/AgentPlanAndExecute.py
Welcome to the Plan-And-Execute AI Agent. Type 'exit' to quit.

>>> Please enter your task:
...
```
