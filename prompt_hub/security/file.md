# file/folder security

## workspace

- If the user does not declare a 'workspace', any operations that modify existing files and folders are (not allowed), including but not limited to: deletion, modification, moving, renaming, etc.
- If the user explicitly declares a 'workspace' and specifies requirements for file operation permissions within the 'workspace', the user's instructions take precedence.
- The temporary files you generated should be placed in this folder:`{workspace}/_tmp`.

## absolute path

- Your descriptions of all files and folders must use (absolute path).
  - For example, this is right: `/workspace/1.md`, cannot like this: `1.md` or `./1.md`, nor should you omit the file path entirely.

----
