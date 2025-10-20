# Additional notes in JSON
The all of (keywords) supported in (JSON) are as follows.
- step_name, string format
- raw_text, string format
- tool_call, specifies the tool name, string format, used only in the action step
- tool_args, specifies tool parameters, JSON format, used only in the action step

Output example:
```
[
  {
    "step_name": "thought",
    "raw_text": "I need to know the OS version"
  },
  {
    "step_name": "action",
    "tool_args": {"cmd_string": "uname -a" },
    "tool_call": "cmd_tool.exec_cmd",
  }
]
```

----
