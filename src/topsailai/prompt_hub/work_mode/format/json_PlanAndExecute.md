# Additional notes in JSON
The all of (keywords) supported in (JSON) are as follows:
- step_name, string format
- raw_text, string format
- tool_call, specifies the tool name, string format, used only in the execute-subtask step
- tool_args, specifies tool parameters, JSON format, used only in the execute-subtask step

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
