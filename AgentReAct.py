#!/usr/bin/env python
# encoding: utf-8

# this is a ai agent, it running in ReAct framework.
# it can think, act, observe and give final answer.
# it can use tool exec_cmd to execute command line in local system.

import os
from dotenv import load_dotenv
import argparse

from ai_base.agent_base import (
    StepCallBase,
    AgentRun,
)
from ai_base.prompt_base import PromptBase
from utils.print_tool import (
    enable_flag_print_step,
    disable_flag_print_step,
)
from tools.cmd_tool import (
    exec_cmd,
)


# define prompt of ReAct framework
SYSTEM_PROMPT_ZH = """
你是一位AI助手。
你需要穿插"thought,action,observation,final_answer"这些步骤去解决任务：
1. thought用于推理当前形势，若最终答案可以确定，则进入final_answer步骤，否则进入action步骤；
2. action用于主动向用户发起请求，你会决定出工具，用户会调用工具；
3. observation是来自用户的答复，你需要观察和分析这个答复，并进入thought步骤。你不能生成“observation”的输出，它只来自用户的输入。
4. final_answer是最终答案，到达这个步骤则问题已经解决。

注意：
- 当你遇到模糊的问题，如，不清楚操作系统版本、命令行工具是否存在等情况，应该进入action步骤去决定出一个工具，从而让用户能够执行，之后你会得到一个来自用户的observation返回。
- 你会对observation的内容进行思考，继续进入thought步骤去推理当前形势，循环往复，直到得到最终答案。
- 当用户没有提出具体问题时，就只有1个thought的回答；否则每次回答必须会有两个内容：1个是thought，1个是action或final_answer。
- 当用户没有声明‘工作空间’，就（不允许）任何改变已有文件和文件夹的操作，包括但不限于：删除、修改、移动、重命名等。
- 当用户明确声明了‘工作空间’，并且对‘工作空间’的文件操作权限做出要求，则以用户为准。

输出格式要求：
1. 所有步骤必须严格使用(JSON)格式输出，当有超过1个输出时使用(list)格式将(json)作为元素按照顺序输出;
```
(JSON)支持的(关键字)如下。
- step_name, 步骤名称，字符串格式
- raw_text, 原始内容，字符串格式
- tool_call, 指定工具名，字符串格式，仅action步骤使用
- tool_args, 指定工具参数，JSON格式，仅action步骤使用
```
2. 当用户(要求)或(想要)输出其它格式，你只能输出到(raw_text)这个关键字中，(不能)改变所有步骤的输出格式。
3. 所有步骤（不能）使用（代码块）格式去输出，包括但不限于：(```)，(```json)等。

输出示例：
```
[
  {
    "step_name": "thought",
    "raw_text": "我需要知道当前操作系统的版本信息，以便确定后续的操作步骤。"
  },
  {
    "step_name": "action",
    "tool_call": "cmd_tool.exec_cmd",
    "tool_args": {"cmd_string": "uname -a" },
    "raw_text": "我将使用exec_cmd工具来获取操作系统的版本信息。"
  }
]
```
"""

SYSTEM_PROMPT = """
You are an AI assistant.
You need to intersperse the steps "thought, action, observation, final_answer" to solve tasks:
1. "thought" is used to reason about the current situation. If the final answer can be determined, proceed to the "final_answer" step; otherwise, proceed to the "action" step.
2. "action" is used to actively initiate a request to the user. You will decide on a tool, and the user will invoke the tool.
3. "observation" is a reply from the user. You need to observe and analyze this reply and proceed to the "thought" step. You cannot generate an output for "observation"; it only comes from the user's input.
4. "final_answer" is the final answer. Reaching this step means the problem has been resolved.

Notes:
- When encountering ambiguous issues, such as unclear operating system versions, whether command-line tools exist, etc., you should proceed to the "action" step to decide on a tool so that the user can execute it. Afterward, you will receive an "observation" response from the user.
- You will reflect on the content of the observation and continue to the "thought" step to reason about the current situation, repeating this cycle until the final answer is obtained.
- If the user does not raise a specific question, there will only be one "thought" response; otherwise, each response must include two components: one "thought" and one "action" or "final_answer."
- If the user does not declare a 'workspace', any operations that modify existing files and folders are (not allowed), including but not limited to: deletion, modification, moving, renaming, etc.
- If the user explicitly declares a 'workspace' and specifies requirements for file operation permissions within the 'workspace', the user's instructions take precedence.

Output format requirements:
1. All steps must strictly use (JSON) format for output. When there is more than one output, use (list) format to output (json) as elements in sequence.
```
The (keywords) supported in (JSON) are as follows.
- step_name, step name, string format
- raw_text, raw content, string format
- tool_call, specifies the tool name, string format, used only in the action step
- tool_args, specifies tool parameters, JSON format, used only in the action step
```
2. When the user (requests) or (wants) to output in other formats, you can only output to the (raw_text) keyword and (cannot) change the output format of all steps.
3. All steps (cannot) use (code block) formats for output, including but not limited to: (```), (```json), etc.

Output example:
```
[
  {
    "step_name": "thought",
    "raw_text": "I need to know the current operating system version information to determine the subsequent steps."
  },
  {
    "step_name": "action",
    "tool_call": "cmd_tool.exec_cmd",
    "tool_args": {"cmd_string": "uname -a" },
    "raw_text": "I will use the exec_cmd tool to retrieve the operating system version information."
  }
]
```
"""

# define global variables
g_flag_interactive = True


class Step4ReAct(StepCallBase):
    """ running on ReAct mode """
    def _execute(self, step:dict, tools:dict, response:list, index:int):
        """ acting steps """
        step_name = step["step_name"]
        if step_name == 'action':
            tool = step['tool_call']
            args = step['tool_args']
            tool_func = tools.get(tool)
            if tool_func is not None:
                obs = tool_func(**args)
                obs_json = {
                    "step_name": "observation",
                    "raw_text": obs
                }
                self.tool_msg = obs_json
                self.code = self.CODE_STEP_FINAL
                return
            else:
                self.result = (f"unknown tool {tool}, exiting.")
                self.code = self.CODE_TASK_FAILED
                return
        elif step_name == "thought":
            if len(response) == 1:
                if not g_flag_interactive:
                    self.code = self.CODE_TASK_FAILED
                    self.result = ("only thought step without action or final_answer in non-interactive mode, exiting.")
                    return
                # interactive mode, ask user for more input
                # only thought, no action or final_answer, ask user for more input
                user_input = input("\n>>> Your input: ")
                self.user_msg = user_input
                self.code = self.CODE_STEP_FINAL
                return
        elif step_name == 'final_answer':
            self.result = step["raw_text"]
            self.code = self.CODE_TASK_FINAL
            return

        return

def get_agent(user_prompt="", to_dump_messages=False):
    """ return a agent object. """
    agent = AgentRun(
        SYSTEM_PROMPT + "\n====\n" + user_prompt,
        tools=None,
        agent_name="AgentReAct",
    )

    # set flags
    if to_dump_messages:
        agent.flag_dump_messages = True

    return agent

def run_once(user_input, to_print_step=None, user_prompt=""):
    """ return final answer, or None if error """
    assert user_input, "user_input is required"
    if to_print_step:
        enable_flag_print_step()
    elif to_print_step is False:
        disable_flag_print_step()

    global g_flag_interactive
    g_flag_interactive = False
    if os.getenv("INTERACTIVE") == "1":
        g_flag_interactive = True

    agent = get_agent(user_prompt)
    final_answer = agent.run(Step4ReAct(), user_input)
    return final_answer

def continue_task(msg_file):
    """ continue a task """
    agent = get_agent()
    agent.load_messages(msg_file)
    final_answer = agent.run(Step4ReAct(), "")
    return final_answer

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
    parser.add_argument(
        "--dump_msg", action="store_true", required=False, dest="flag_dump_messages",
        default=False,
        help="dump all of messages to a file"
    )
    parser.add_argument(
        "--msg_file", required=False, dest="msg_file", type=str,
        default=None,
        help="use the msg_file to continue a task"
    )
    args = parser.parse_args()
    params = {
        "prompt_file": args.prompt_file,
        "prompt_content": "",
        "task": args.task,
        "flag_dump_messages": args.flag_dump_messages,
        "msg_file": args.msg_file,
    }

    # get prompt content
    if params["prompt_file"]:
        with open(params["prompt_file"], "r") as fd:
            params["prompt_content"] = fd.read() or ""

    # set flags
    if params["flag_dump_messages"]:
        PromptBase.flag_dump_messages = True

    return params


def main():
    """ return nothing """
    load_dotenv()  # load environment variables from .env file if present

    params = get_params()

    # continue a task
    if params["msg_file"]:
        final_answer = continue_task(params["msg_file"])
        if final_answer:
            print(f"\n>>> Final Answer:\n{final_answer}")
        else:
            print("Failed to get a final answer.")
        return

    # run once mode
    if params["task"]:
        final_answer = run_once(
            user_input=params["task"],
            user_prompt=params["prompt_content"]
        )
        if final_answer:
            print(f"\n>>> Final Answer:\n{final_answer}")
        else:
            print("Failed to get a final answer.")
        return

    # interactive mode
    agent = get_agent(params["prompt_content"])
    print("Welcome to the AI Agent Shell. Type 'exit' to quit.")
    while True:
        user_input = input("\n>>> Enter your task: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        if user_input.strip() == "":
            continue
        final_answer = agent.run(Step4ReAct(), user_input)
        if final_answer:
            print(f"\nFinal Answer: {final_answer}")
        else:
            print("Failed to get a final answer.")
    return

if __name__ == "__main__":
    main()
