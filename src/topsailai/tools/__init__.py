'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-18
  Purpose: import all of tools to support AI-Agent.
'''

import os

from topsailai.utils import (
    module_tool,
    format_tool,
    print_tool,
)

# key is tool_name, value is function
TOOLS = module_tool.get_function_map("topsailai.tools", "TOOLS")

# key is tool_name, value is dict
# Value Example:
# {
#     "type": "function",
#     "function": {
#         "name": "get_current_weather",
#         "description": "获取指定城市的当前天气",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "location": {
#                     "type": "string",
#                     "description": "城市名称"
#                 },
#                 "unit": {
#                     "type": "string",
#                     "enum": ["celsius", "fahrenheit"],
#                     "description": "温度单位"
#                 }
#             },
#             "required": ["location"]
#         }
#     }
# }
TOOLS_INFO = module_tool.get_function_map("topsailai.tools", "TOOLS_INFO")


TOOL_PROMPT = """
---
# TOOLS
Attention: You MUST use the tool name (completely), e.g. whole name is 'x_tool.y_func', you cannot use 'y_func'.
{__TOOLS__}
---
"""

def get_tool_prompt(tools_name:list=None, tools_map:dict=None):
    """
    :tools_name: list_str;
    :tools_map: dict, key is tool name, value is function.

    return tool_prompt for tools """
    tools_doc = {}

    if tools_name:
        for tool_name in format_tool.to_list(tools_name, to_ignore_none=True):
            tools_doc[tool_name] = TOOLS[tool_name].__doc__

    if tools_map:
        for tool_name, tool_func in tools_map.items():
            tools_doc[tool_name] = tool_func.__doc__

    if not tools_doc:
        return ""

    return TOOL_PROMPT.format(
        __TOOLS__=print_tool.format_dict_to_md(tools_doc)
    )

def expand_plugin_tools():
    """ expand tools by external plugins """
    env_plugin_tools = os.getenv("PLUGIN_TOOLS")
    if not env_plugin_tools:
        return
    for plugin_path in env_plugin_tools.split(';'):
        _tools = module_tool.get_external_function_map(plugin_path, "TOOLS")
        if _tools:
            TOOLS.update(_tools)

        _tools_info = module_tool.get_external_function_map(plugin_path, "TOOLS_INFO")
        if _tools_info:
            TOOLS_INFO.update(_tools_info)

    return

def generate_tool_info(tool_name, tool_description):
    result = {
        "type": "function",
        "function": {
            "name": tool_name,
            "description": tool_description,
            "parameters": {
                "type": "object",
            }
        }
    }
    return result

def get_tools_for_chat(tools_name:list[str]) -> dict:
    """ return tools info """
    result = {}
    for tool_name in tools_name:
        if tool_name in TOOLS_INFO:
            result[tool_name] = TOOLS_INFO[tool_name]
            result[tool_name]["function"]["name"] = tool_name
            continue
        if tool_name in TOOLS:
            result[tool_name] = generate_tool_info(tool_name, TOOLS[tool_name].__doc__)

    return result


# init
expand_plugin_tools()
