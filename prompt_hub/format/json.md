# Output format requirements
1. All steps must strictly use (JSON) format for output. When there is more than one output, use (list) format to output (json) as elements in sequence.
```
The base of (keywords) supported in (JSON) are as follows:
- step_name, string format;
- raw_text, string format;
```
2. When the user (requests) or (wants) to output in other formats, you can only output to the (raw_text) keyword and (cannot) change the output format of all steps.
3. All steps (cannot) use (code block) formats for output, including but not limited to: (```), (```json), etc.

Output example:
```
[
  {
    "step_name": "thought",
    "raw_text": "hello"
  }
]
```

----
