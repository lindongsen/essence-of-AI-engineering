'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-18
  Purpose: import all of tools to support AI-Agent.
'''

import os
import simplejson

from topsailai.utils import (
    module_tool,
    format_tool,
)

# key is tool_name, value is function
TOOLS = module_tool.get_function_map("topsailai.tools")

TOOL_PROMPT = """
----

# tools
The tool information is described in JSON below, key is tool name, value is tool document.
Attention: You MUST use the tool name (completely), e.g. whole name is 'cmd_tool.exec_cmd', you cannot use 'exec_cmd'.
```
{__TOOLS__}
```

----
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
        __TOOLS__=simplejson.dumps(tools_doc, indent=2, ensure_ascii=False)
    )

def expand_plugin_tools():
    """ expand tools by external plugins """
    env_plugin_tools = os.getenv("PLUGIN_TOOLS")
    if not env_plugin_tools:
        return
    for plugin_path in env_plugin_tools.split(';'):
        _tools = module_tool.get_external_function_map(plugin_path)
        if _tools:
            TOOLS.update(_tools)
    return


# init
expand_plugin_tools()
