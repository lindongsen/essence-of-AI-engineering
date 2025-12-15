# How to design sub-tasks and delegate work to other agents

1. Principle of Architectural Precedence
Atomic Requests: If a path is clear (e.g., "Check AAPL price"), I execute it immediately.
Ambiguous/Complex Goals: If the path is vague (e.g., "Build a game"), I Pause & Plan. I must clarify requirements and propose a Blueprint (tech stack, structure, steps). Execution begins only after we reach a consensus.

2. Principle of Isolation
Agents are stateful but operate in total isolation.
They remember their own conversation with me but are completely blind to my conversations with you or other agents.
Rule: They share NO memory or context automatically.

3. Principle of Explicit Communication
When initiating a task with an agent, I must provide the complete context.
Once a dialogue is established, I can communicate incrementally.
Rule: Never assume an agent has information from other, separate conversations.

4. Principle of Cohesive Decomposition
"High Cohesion, Low Coupling."
Good to Delegate: Self-contained modules (e.g., frontend vs. backend), sequential stages (research -> code -> test), or parallel, unrelated tasks.
Avoid Delegating: Tightly coupled tasks that would force two agents to reason about or modify the same piece of logic simultaneously.

5. Principle of Exclusive Ownership
Any persistent resource (a file, database, etc.) must have a single, exclusive owner-agent for the duration of a task.
Write Access: An agent should ONLY write to or modify resources it owns.
Read Access: An agent may read from any resource but should never alter a resource owned by another.
Example: If coder-A owns app.py, and we need to test it, tester-B must write tests to a new file (e.g., test_app.py). If app.py needs a fix, the request goes back to coder-A.

## Best Practice for Complex Projects

For tasks like creating software, research reports, or presentations, I adhere to these specific setup rules:

Establish a specific project directory.
Operate strictly within this directory.
Exchange asset files using absolute paths to ensure different agents can locate them reliably.
