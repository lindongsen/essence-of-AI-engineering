# Context Management for File Operations

Core Principle: When calling tools or executing commands, efforts should be made to avoid generating large text content outputs.

## Specific Optimization Strategies

- [Attention] When the output content is too long, it will be forcibly truncated, and the flag information is "(force to truncate)". At this time, you should consider other ways for the data.

### File Content Inspection

- When the user hasn't explicitly requested a full-content inspection, only read partial content during file checks.
  - Example: For text material inspection, only read the first 100 bytes. Applicable commands: `head -c 100 file`, `tail -c 100 file`.

### Command Output Control

- Ignore stderr content when using:
  - curl, Example `curl https://example.com 2>/dev/null`;
  - `uv add`, Example `uv add pip 2>/dev/null`;

### Temporary File Utilization

- Save results to temporary files when not all tool output needs attention
- Read partial content from temporary files for inspection
- Promptly clean up temporary resources after inspection completion

## Practical Example

- When checking the readability of file `/f.txt`:
```
# Check only the first and last 100 bytes each
head -c 100 /f.txt
tail -c 100 /f.txt
```

----
