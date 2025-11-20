'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-18
  Purpose:
'''

import os
import threading

from logger import logger
from utils.json_tool import json_dump, json_load
from utils.format_tool import to_list


def get_all_agent_tools():
    """ return dict, key is tool_name, value is tool_func. """
    from . import TOOLS as INTERNAL_TOOLS

    agent_tools = {}
    for tool_name, tool_func in INTERNAL_TOOLS.items():
        if tool_name.startswith("agent"):
            agent_tools[tool_name] = tool_func
    return agent_tools

def agent_writer(msg_or_file:str, model_name:str=None, workspace:str="/workspace"):
    """ A professional Assistant for writer.
    The writing assistant can read a large amount of text content.
    There are no restrictions for scenarios that may generate substantial text,
    such as reading large files or fetching web content via cURL.
    The text will not be forcibly truncated.

    # parameters
    :msg_or_file: string, can be message or file path.
        if user pass a file path, the content of the file will be read as message.
        if the user does explicitly specify a file, should use it directly.

    :model_name: LLM name, If the user does not explicitly specify, this parameter is not needed.
    :workspace: a folder absolute path for workspace.

    # return
    return final answer.
    """
    message = msg_or_file
    # read message from file if msg_or_file is a file path
    if msg_or_file[0] in ["/", "."]:
        if os.path.isfile(msg_or_file):
            with open(msg_or_file, "r", encoding="utf-8") as f:
                message = f.read()

    workspace = workspace.strip()
    if workspace:
        if 'workspace' not in message or '工作空间' not in message:
            message += f"\n----\nworkspace:`{workspace}`\n"

    from ai_base.agent_base import AgentRun
    from AgentReAct import SYSTEM_PROMPT, Step4ReAct

    agent = AgentRun(
        system_prompt=SYSTEM_PROMPT + "\nYou are a professional writer.\n",
        tools=None,
        agent_name="AgentWriter",
        excluded_tool_kits=get_all_agent_tools().keys(),
    )
    if not model_name:
        model_name = "DeepSeek-V3.1"
    agent.llm_model.openai_model_name = model_name
    return agent.run(Step4ReAct(), message)

def agent_programmer(
        msg_or_file:str, model_name:str=None, workspace:str="/workspace",
        system_prompt:str="",
    ):
    """ A professional Assistant for programmer.

    # parameters
    :msg_or_file: string, it can be message or file path for a TASK.
        if user pass a file path, the content of the file will be read as message.
        if the user does explicitly specify a file, should use it directly.

    :model_name: LLM name, If the user does not explicitly specify, this parameter is not needed.
    :workspace: a folder absolute path for workspace.
    :system_prompt: string, it can be content or a filepath; If the user does not explicitly specify, this parameter is not needed.

    # return
    return final answer.
    """
    message = msg_or_file
    # read message from file if msg_or_file is a file path
    if msg_or_file[0] in ["/", "."]:
        if os.path.isfile(msg_or_file):
            with open(msg_or_file, "r", encoding="utf-8") as f:
                message = f.read()

    workspace = workspace.strip()
    if workspace:
        if 'workspace' not in message or '工作空间' not in message:
            message += f"\n----\nworkspace:`{workspace}`\n"

    # system prompt
    if system_prompt and system_prompt[0] in ["/", "."]:
        if os.path.isfile(system_prompt):
            with open(system_prompt, encoding="utf-8") as fd:
                system_prompt = fd.read()

    from ai_base.agent_base import AgentRun
    from AgentReAct import SYSTEM_PROMPT, Step4ReAct
    agent = AgentRun(
        system_prompt=SYSTEM_PROMPT + system_prompt + "\nYou are a professional programmer.\n",
        tools=None,
        agent_name="AgentProgrammer",
        excluded_tool_kits=get_all_agent_tools().keys(),
    )
    if not model_name:
        model_name = "DeepSeek-V3.1"
    agent.llm_model.openai_model_name = model_name
    return agent.run(Step4ReAct(), message)

def async_multitasks_agent_writer(
        goal:str,
        goal_report_file:str=None,
        task_prompt_file:str=None, model_name:str=None, workspace:str="/workspace", **tasks
    ):
    """ A professional writing assistant capable of executing tasks concurrently.

    # Example:
    WritingAssistantMultiTasks(
        goal={GOAL OR PLAN},
        goal_report_file={REPORT_FILE_PATH},
        task_prompt_file={FILE_PATH},
        model_name={LLM_NAME},
        workspace={FOLDER},
        task1={TASK1},
        task2={TASK2},
    )

    # parameters
    :goal: one goal, multiple tasks;
        These tasks will be executed concurrently by WritingAssistant;
        Finally, the goal will be called to summarize the execution results of these tasks.
    :goal_report_file: the file path for saving the final report of this goal.
    :task_prompt_file: a file path; This document is a supplementary explanation or task requirements.
    :tasks: multiple args, format is 'key=value', value can be message or file path, key prefix name is 'task', example: task1=xxx, task2=yyy;
        if user pass a file path, the content of the file will be read as message.
        if the user does explicitly specify a file, should use it directly.

    :model_name: LLM name, If the user does not explicitly specify, this parameter is not needed.
    :workspace: a folder absolute path for workspace.

    # return
    return final answer.
    """
    thrs = {}
    results = {}

    # thread control
    semaphore = threading.Semaphore(10)

    task_prompt = ""
    if task_prompt_file and os.path.exists(task_prompt_file):
        with open(task_prompt_file, encoding="utf-8") as fd:
            task_prompt = fd.read()

    if task_prompt:
        task_prompt += "\n\n----\n\n"

    def _execute_task(_key, *args, **kwargs):
        with semaphore:
            result = agent_writer(
                *args, **kwargs
            )
            results[_key]["result"] = result
        return

    for k, v in tasks.items():
        v = str(v)
        results[k] = {
            "task": v,
            "result": "task failed"
        }
        if k.lower().startswith("task"):
            thr = threading.Thread(
                name=f"async_multitasks_agent_writer.{k}",
                daemon=False,
                target=_execute_task,
                kwargs=dict(
                    _key=k,
                    msg_or_file=task_prompt + v,
                    model_name=model_name,
                    workspace=workspace,
                )
            )
            thrs[k] = thr
            thr.start()

    # wait all threads done
    for k, t in thrs.items():
        logger.info(f"task is running: [{k}]")
        t.join()
        logger.info(f"task is done: [{k}]")

    if goal[0] not in ["/", "."]:
        goal += (
            "\n\n----\n\n"
            + (f"saving the final report to the file:{goal_report_file}\n\n" if goal_report_file else "")
            + json_dump(results, indent=0)
            + "\n\n"
        )

    return agent_writer(goal, model_name=model_name, workspace=workspace)


def async_multitasks_agent_writer2(
        goal:str,
        goal_report_file:str,
        task_prompt_file:str,
        tasks_file_or_json:str,
        model_name:str=None,
        workspace:str="/workspace"
    ):
    """ A professional writing assistant capable of executing tasks concurrently.

    one goal, multiple tasks:
        These tasks will be executed concurrently by WritingAssistant;
        Finally, the goal will be called to summarize the execution results of these tasks.

    # Example:
    WritingAssistantMultiTasks(
        goal={GOAL OR PLAN},
        goal_report_file={REPORT_FILE_PATH},
        task_prompt_file={PROMPT_FILE_PATH},
        tasks_file_or_json={TASKS_FILE_PATH} or {JSON_STRING},
        model_name={LLM_NAME},
        workspace={FOLDER}
    )

    # parameters
    :goal: string, one goal.
    :goal_report_file: the file path for saving the final report of this goal.
    :task_prompt_file: a file path; This document is a supplementary explanation or task requirements.
    :tasks_file_or_json: a file path or a json string, if file path, its content is json string;
        The JSON string is a list, and this list is a collection of tasks.

    :model_name: LLM name, If the user does not explicitly specify, this parameter is not needed.
    :workspace: a folder absolute path for workspace.

    # return
    return final answer.
    """
    tasks_content = tasks_file_or_json
    if tasks_file_or_json[0] in ["/", "."]:
        with open(tasks_file_or_json, encoding="utf-8") as fd:
            tasks_content = fd.read()
    assert tasks_content
    tasks = json_load(tasks_content)
    tasks_kv = {}
    for i, task in enumerate(to_list(tasks)):
        tasks_kv[f"task{i}"] = task

    return async_multitasks_agent_writer(
        goal=goal,
        goal_report_file=goal_report_file,
        task_prompt_file=task_prompt_file,
        model_name=model_name,
        workspace=workspace,
        **tasks_kv
    )


TOOLS = dict(
    WritingAssistant=agent_writer,
    ProgrammingAssistant=agent_programmer,
    WritingAssistantMultiTasks=async_multitasks_agent_writer2,
)
