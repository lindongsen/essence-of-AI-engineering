#!/usr/bin/env python

# this is a ai agent, it running in Plan-And-Execute framework.
# it can plan a task into multiple sub-tasks, and execute them one by one.
# it can use tool agent_shell to execute single sub-task.

from dotenv import load_dotenv

from ai_base.agent_base import (
    StepCallBase,
    AgentRun,
)

import AgentReAct

# define roles
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
ROLE_SYSTEM = "system"
ROLE_TOOL = "tool"

# define prompt of Plan-And-Execute framework
SYSTEM_PROMPT = """
你的核心职责是将用户提供的“高级任务”分解为可操作的子任务，制定一个循序渐进的计划，然后协调执行这些子任务。
你有一个辅助工具AgentShell，它可以执行单一、具体的任务。
你的输出应包括完整的计划概述、每个步骤的执行结果以及最终总结。

严格遵循以下步骤：
0. 任务提交(task)：用户会提交一个任务。当用户没有提交任务或任务模糊，请向用户发起询问（task-ask），用户会答复给你task。
1. 任务分析(plan-analysis)：分析任务描述，理解任务目标、上下文信息、任何约束条件。如果任务模糊，请向用户发起询问（task-ask）。
2. 任务规划(plan-list)：分解任务为自然语言描述的一个或多个逻辑子任务（subtasks），这些子任务是有顺序的，每个子任务是原子性的，确保它们组合起来能实现总体目标。
3. 执行（execute-subtask）:按顺序执行子任务，调用AgentShell来执行单一子任务。等待单一子任务执行完毕，获得子任务的执行结果（subtask-result）。
4. 重新规划（replan-list）:你已经知道当前子任务执行到哪一步，需要再根据‘subtask-result’和‘subtasks’重新做任务规划，生成新的subtasks。任务规划方式同上述的plan-list步骤。
5. 执行（execute-subtask）:同上述的execute-subtask步骤。
6. 最终结果（final）:所有子任务执行完毕后，将所有子任务的结果组合起来，生成最终输出，确保输出符合用户的原始任务目标。

特别注意：
- 在plan-list和replan-list这两个步骤中，当你遇到模糊的问题，例如：不清楚操作系统版本、相关工具是否存在等情况，应该将这类模糊事件规划成子任务去做确定。
- 当你‘不理解’任务目标，则输出中必须有task-ask，否则输出中必须有且仅有一个‘execute-subtask或final’。
- 子任务不允许任何改变已有文件和文件夹的操作，包括但不限于：删除、修改、移动、重命名等。

输出格式要求：
所有步骤必须严格使用JSON的格式输出，当有超过1个输出时使用list格式将json作为元素按照顺序输出，JSON支持的关键字如下。
- step_name, 步骤名称，字符串格式
- raw_text, 原始内容，字符串格式
- tool_call, 指定工具名，字符串格式，仅execute-subtask步骤使用
- tool_args, 指定工具参数，JSON格式，仅execute-subtask步骤使用

----

AgentShell的调用方式：
- agent_shell(message)，返回JSON，如{"step_name":"subtask_result","raw_text":"ok"}。

----

"""

def agent_shell(message):
    """ return dict """
    final_answer = AgentReAct.run_once(message)
    return {"step_name":"subtask_result","raw_text":final_answer}

class StepCall4PlanAndExecute(StepCallBase):
    """ running on Plan-And-Execute mode """
    def _execute(self, step:dict, tools:dict, response:list, index:int):
        """ acting steps """
        step_name = step.get("step_name", "")
        raw_text = step.get("raw_text", "")
        tool_call = step.get("tool_call", "")
        tool_args = step.get("tool_args", {})

        if step_name == "final":
            self.result = raw_text
            self.code = self.CODE_TASK_FINAL
            return

        elif step_name == "task-ask":
            # Ask user for more information
            user_reply = input(f">>> LLM: {raw_text}\n>>> Your input: ")
            self.user_msg = {"step_name":"task","raw_text":user_reply}
            self.code = self.CODE_STEP_FINAL
            return

        elif step_name == "execute-subtask":
            if tool_call in tools:
                tool_func = tools[tool_call]
                result = tool_func(**tool_args)
                self.tool_msg = result
                self.code = self.CODE_STEP_FINAL
                return
            else:
                self.result = (f"Unknown tool call {tool_call}.")
                self.code = self.CODE_TASK_FAILED
                return

        return

def main():
    """ return nothing """
    load_dotenv()  # load environment variables from .env file if present

    # interactive mode
    agent = AgentRun(
        SYSTEM_PROMPT,
        tools={"agent_shell": agent_shell},
        agent_name="AgentPlanAndExecute",
    )
    print("Welcome to the Plan-And-Execute AI Agent. Type 'exit' to quit.")
    while True:
        user_input = input("\n>>> Enter your task: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting. Goodbye!")
            break
        if not user_input.strip():
            continue
        final_answer = agent.run(StepCall4PlanAndExecute(), user_input)
        if final_answer:
            print(f"\n>>> Final Answer: {final_answer}")
        else:
            print("Failed to get a final answer.")
    return

if __name__ == "__main__":
    main()
