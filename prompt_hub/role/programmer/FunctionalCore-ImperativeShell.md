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

## Code Structure Management

All modules must be organized into three categories according to folders, referred to as the "Three-Category Partitioning Principle":

1. **Pure Functional Core** (functional_core);

2. **Imperative Let Shell** (let_shell): Executes clear business commands with unambiguous content, avoiding functional branching.
   Example: Creating a qcow2 image file at a specific file path.

3. **Procedural Shell** (procedural_shell): Executes specific business processes where tasks may be ambiguous and may involve execution branches such as "factory patterns" or "adapters."
   Example: Creating a qcow2 image file, where a parameter may indicate it could be created either locally or on another storage path.

The imperative shell can be extended further outward,
e.g., a `handler_shell` used to respond to the first layer of API programs,
forming the call chain: `handler_shell -> component.procedural_shell -> module.procedural_shell -> module.let_shell -> module.functional_core`.

The code structure of modules, components, and the entire project will follow the "Three-Category Partitioning Principle."
Some common methods can be stored in dedicated folders, such as `common`, which also adhere to the "Three-Category Partitioning Principle."

Example:
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
    └── handler_shell

[Attention] File/Folder naming should be adapted according to the actual project situation.
```

----
