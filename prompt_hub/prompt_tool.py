'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-20
  Purpose:
'''

import os

def get_extra_tools():
    """
    return string for prompt content of extra tools
    """
    result = ""
    extra_tools = os.getenv("EXTRA_TOOLS")
    if extra_tools:
       # split by ';'
       extra_tools = extra_tools.split(';')
    for tool_prompt_file in extra_tools:
        tool_prompt_file = tool_prompt_file.strip()
        if not tool_prompt_file:
            continue
        if not os.path.exists(tool_prompt_file):
            continue
        result += read_prompt(tool_prompt_file)
    result = result.strip()
    if not result:
        return ""
    return \
    f"""
# Extra Tools Start

{result}

# Extra Tools End
---
"""

def read_prompt(relative_path):
    """ return string for file content.

    :relative_path: e.g. 'format/json.md'
    """
    file_path = relative_path
    if not os.path.exists(file_path):
        file_path = os.path.join(
            os.path.dirname(__file__), relative_path
        )
    with open(file_path) as fd:
        content = fd.read().strip()
        if content:
            # add split line to tail
            if content.endswith("====") or content.endswith("----"):
                content += "\n"
            else:
                content += "\n----\n\n"
            return content

    return ""


class PromptHubExtractor(object):
    """ a extractor to get prompt """

    # basic
    prompt_common = (
        read_prompt("security/file.md")
        + read_prompt("context/file.md")
        + read_prompt("search/text.md")
        + read_prompt("project/folder.md")
    )

    # task management
    prompt_task = (
        read_prompt("task/control.md")
        + read_prompt("task/tracking.md")
    )

    # interactive, json
    prompt_interactive_json = read_prompt("format/json.md")

    # work-mode ReAct
    prompt_mode_ReAct = (
        read_prompt("work_mode/ReAct.md")
        + prompt_common
        + prompt_task

        # place them to tail
        + prompt_interactive_json
        + read_prompt("format/json_ReAct.md")
    )

    # work-mode PlanAndExecute
    prompt_mode_PlanAndExecute = (
        read_prompt("work_mode/PlanAndExecute.md")
        + prompt_common
        + prompt_task

        # place them to tail
        + prompt_interactive_json
        + read_prompt("format/json_PlanAndExecute.md")
    )
