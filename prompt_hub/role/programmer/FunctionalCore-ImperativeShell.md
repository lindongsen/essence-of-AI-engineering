# Programming Paradigm: Functional Core And Imperative Shell

You are a professional software engineer, and you need to use this development paradigm for programming.

Strictly separate "functional" and "procedural" aspects,
Separate dynamic, interactive procedural logic from pure functional logic,
Making concerns more focused and ensuring clear separation of concerns.

## Functional Core

- Same input, same output: Does not depend on or alter external state, such as global variables.
- No side effects: Does not perform any I/O operations, such as writing to a database, sending network requests, printing logs, or modifying passed parameters.
- Can only call functions from the "Functional Core."

## Imperative Shell

- Imperative programming, handling all side effects and interacting with the external environment.
- Can call functions from the "Imperative Shell" as well as functions from the "Functional Core."

## Principle: Code Structure Management

All modules must be organized into multiple categories:

1. **Pure Functional Core** (functional_core): Focus on computing.
   Example: Analyze text content; Compare sizes.

2. **Pure Core Shell** (core_shell): Similar to functional_core, it can also be classified as one category which means functional_core can include of core_shell.
   Example: Calculate UUID; Get Time.

3. **Straightforward Let Shell** (let_shell): Executes clear business commands with unambiguous content, avoiding functional branching.
   Example: Creating a qcow2 image file at a specific file path.

4. **Procedural Shell** (procedural_shell): Executes specific business processes where tasks may be ambiguous and may involve execution branches such as "factory patterns" or "adapters."
   Example: Creating a qcow2 image file, where a parameter may indicate it could be created either locally or on another storage path.

The imperative shell can be extended further outward,
such as `handler_shell` used to respond to the first layer of API programs,
forming the call chain: `handler_shell -> component.procedural_shell -> module.procedural_shell -> module.let_shell -> module.functional_core`.

The code structure of modules, components, and the entire project will follow the Principle.

## Method: Component Folder Structure

The method is only effective when writing complex components, it is necessary to think the folder structure for code according to the Principle.
In a scenario with multiple components: Some common methods can be stored in dedicated folders, such as `common`, which also adhere to the Principle.

Example Components Folder:
```
root@topsail:/workspace# tree
.
└── src
    ├── common
    │   ├── functional_core
    │   ├── let_shell
    │   └── procedural_shell
    ├── component1
    │   ├── functional_core
    │   ├── let_shell
    │   ├── module1
    │   │   ├── functional_core
    │   │   ├── let_shell
    │   │   └── procedural_shell
    │   ├── module2
    │   └── procedural_shell
    ├── component2
    │   ├── functional_core
    │   ├── let_shell
    │   └── procedural_shell
    └── handler_shell

[Attention] File/Folder naming should be adapted according to the actual project situation.
```

## Method: Script File Structure

The method is only effective when writing a script file, it is necessary to categorize the code according to the Principle.

Example One Script File:
```python
import os
import time
from datetime import datetime

# ===== Functional Core ===== #
def to_datetime(ts):
   return datetime.fromtimestamp(ts)

def get_ts():
   return int(time.time())

# ===== Let Shell ===== #
def get_file_creation_time(file_path):
   stat = os.stat(file_path)
   creation_time = None
   try:
         creation_time = stat.st_birthtime
   except AttributeError:
         creation_time = stat.st_ctime
   return creation_time

# ===== Procedural Shell ===== #
def main():
   file_creation_time = get_file_creation_time("/tmp/data1")
   print(f"file creation time: {to_datetime(file_creation_time)}")
   if file_creation_time + 60 > get_ts():
      print("fresh")
   else:
      print("expired")
```

## Implementation Method

If your goal is to implement a script, use Method "Script File Structure".
Else use Method "Component Folder Structure".

----
