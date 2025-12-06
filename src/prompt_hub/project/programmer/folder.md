# Project Folder

This (Project Folder) method is only effective when `workspace` and `project_name` are explicitly defined.

- You should place all of the generated code inside `{workspace}/{project_name}`.
- The relevant folders need to be created in advance.

## project folder structure

It should include the following:

- folder: `cli`, store script files
- folder: `src`, store source code files
- folder: `tests`, store test files
- file: `README.md`, save detail info about of the project

## Python Project Management

Use the uv tool to manage the project:

- Initialize project: `uv init`. You cannot create or edit the configuration file `pyproject.toml` - it must be managed exclusively by the uv tool itself.
- Add dependency: `uv add {package_name}`
- Remove dependency: `uv remove {package_name}`
- Execute command: `uv run {python_file_or_command}`
