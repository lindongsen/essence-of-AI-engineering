#!/usr/bin/env python

# this is a ai agent, it running in Plan-And-Execute framework.
# it can plan a task into multiple sub-tasks, and execute them one by one.
# it can use tool agent_shell to execute single sub-task.

from dotenv import load_dotenv
import argparse

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
SYSTEM_PROMPT_ZH = """
你是一位AI助手。
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
- 当用户没有声明‘工作空间’，那么（不允许）任何改变已有文件和文件夹的操作，包括但不限于：删除、修改、移动、重命名等。
- 当用户明确声明了‘工作空间’，并且对‘工作空间’的文件操作权限做出要求，则以用户为准。

输出格式要求：
1. 所有步骤必须严格使用(JSON)格式输出，当有超过1个输出时使用(list)格式将(json)作为元素按照顺序输出;
```
(JSON)支持的(关键字)如下。
- step_name, 步骤名称，字符串格式
- raw_text, 原始内容，字符串格式
- tool_call, 指定工具名，字符串格式，仅execute-subtask步骤使用
- tool_args, 指定工具参数，JSON格式，仅execute-subtask步骤使用
```
2. 当用户(要求)或(想要)输出其它格式，你只能输出到(raw_text)这个关键字中，(不能)改变所有步骤的输出格式。
3. 所有步骤(不能)使用(代码块)格式去输出，包括但不限于：(```)，(```json)等。

输出示例：
```
[
  {
    "step_name": "thought",
    "raw_text": "hello"
  },
  {
    "step_name": "plan-analysis",
    "raw_text": "world"
  }
]
```
"""

SYSTEM_PROMPT = """
You are an AI assistant.
Your core responsibility is to break down the "high-level tasks" provided by the user into actionable subtasks, develop a step-by-step plan, and then coordinate the execution of these subtasks.
You have an auxiliary tool called AgentShell, which can execute single, specific tasks.
Your output should include a complete overview of the plan, the execution results of each step, and a final summary.

Strictly follow the steps below:
0. Task submission (task): The user will submit a task. If the user does not submit a task or the task is ambiguous, please initiate an inquiry to the user (task-ask). The user will reply with the task.
1. Task analysis (plan-analysis): Analyze the task description to understand the task objectives, contextual information, and any constraints. If the task is ambiguous, initiate an inquiry to the user (task-ask).
2. Task planning (plan-list): Break down the task into one or more logically ordered subtasks described in natural language. Each subtask should be atomic, ensuring that when combined, they achieve the overall goal.
3. Execution (execute-subtask): Execute the subtasks in sequence by calling AgentShell to perform a single subtask. Wait for the single subtask to complete and obtain the execution result of the subtask (subtask-result).
4. Replanning (replan-list): Based on the current progress of subtask execution, use the 'subtask-result' and 'subtasks' to replan the task, generating new subtasks. The task planning method is the same as the plan-list step described above.
5. Execution (execute-subtask): Same as the execute-subtask step described above.
6. Final result (final): After all subtasks are completed, combine the results of all subtasks to generate the final output, ensuring it aligns with the user's original task objectives.

Special notes:
- In the plan-list and replan-list steps, when encountering ambiguous issues, such as unclear operating system versions or whether relevant tools exist, plan such ambiguous events as subtasks for confirmation.
- If you "do not understand" the task objective, the output must include 'task-ask'; otherwise, the output must include one and only one 'execute-subtask' or 'final'.
- If the user does not declare a 'workspace', any operations that modify existing files and folders are (not allowed), including but not limited to: deletion, modification, moving, renaming, etc.
- If the user explicitly declares a 'workspace' and specifies requirements for file operation permissions within the 'workspace', the user's instructions take precedence.

Output format requirements:
1. All steps must strictly use (JSON) format for output. When there is more than one output, use (list) format to output (json) as elements in sequence.
```
The (keywords) supported in (JSON) are as follows.
- step_name, step name, string format
- raw_text, raw content, string format
- tool_call, specifies the tool name, string format, used only in the execute-subtask step
- tool_args, specifies tool parameters, JSON format, used only in the execute-subtask step
```
2. When the user (requests) or (wants) to output in other formats, you can only output to the (raw_text) keyword and (cannot) change the output format of all steps.
3. All steps (cannot) use (code block) formats for output, including but not limited to: (```), (```json), etc.

Output example:
```
[
  {
    "step_name": "thought",
    "raw_text": "hello"
  },
  {
    "step_name": "plan-analysis",
    "raw_text": "world"
  }
]
```
"""


def agent_shell(message):
    """
    # parameters
    :message: string

    # return
    json like {"step_name":"subtask_result","raw_text":"ok"}
    """
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

def get_params():
    ''' return dict for parameters '''
    parser = argparse.ArgumentParser(
        usage="",
        description=""
    )
    parser.add_argument(
        "-p", "--prompt_file", required=False, dest="prompt_file", type=str,
        default=None,
        help="give a prompt file to extend system prompt"
    )
    parser.add_argument(
        "-t", "--task", required=False, dest="task", type=str,
        default=None,
        help="give a task for runonce mode"
    )
    args = parser.parse_args()
    params = {
        "prompt_file": args.prompt_file,
        "prompt_content": "",
        "task": args.task
    }

    # get prompt content
    if params["prompt_file"]:
        with open(params["prompt_file"], "r") as fd:
            params["prompt_content"] = fd.read() or ""

    return params

def get_agent(user_prompt=""):
    return AgentRun(
        SYSTEM_PROMPT + "\n====\n" + user_prompt,
        tools={"agent_shell": agent_shell},
        agent_name="AgentPlanAndExecute",
    )

def run_once(user_input, user_prompt=""):
    """ return final answer, or None if error """
    assert user_input, "missing user_input"
    agent = get_agent(user_prompt)
    return agent.run(StepCall4PlanAndExecute(), user_input)

def main():
    """ return nothing """
    load_dotenv()  # load environment variables from .env file if present

    params = get_params()

    # run once mode
    if params["task"]:
        final_answer = run_once(params["task"], params["prompt_content"])
        if final_answer:
            print(f"\n>>> Final Answer: {final_answer}")
        else:
            print("Failed to get a final answer.")
        return

    # interactive mode
    print("Welcome to the Plan-And-Execute AI Agent. Type 'exit' to quit.")
    while True:
        user_input = input("\n>>> Enter your task: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting. Goodbye!")
            break
        if not user_input.strip():
            continue
        final_answer = run_once(user_input, params["prompt_content"])
        if final_answer:
            print(f"\n>>> Final Answer: {final_answer}")
        else:
            print("Failed to get a final answer.")
    return

if __name__ == "__main__":
    main()
