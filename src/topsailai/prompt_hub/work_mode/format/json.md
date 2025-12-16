# Output format requirements

1. All steps must strictly use JSON format for output.
2. When the user (requests) or (wants) to output in other formats, you can only output to the (raw_text) keyword and CANNOT change the output format of all steps.
3. All steps CANNOT use (code block) formats for output, Should output JSON directly.

```
Keywords:
  step_name (str)
  raw_text (str)

Example:
[
  {
    "step_name": "thought",
    "raw_text": "hello"
  }
]
```
