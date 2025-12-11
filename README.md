# Tredence-APP
# Workflow Engine Assignment

This project is a simple backend workflow engine built with FastAPI. It lets you define a set of steps (nodes), connect them in a graph, share state between them, and run the workflow end-to-end through APIs. It follows the requirements given in the assignment PDF: a minimal graph engine, a tool registry, FastAPI endpoints, and one example agent workflow.

## Project structure

The main code lives in the `app` folder:

- `app/main.py` – FastAPI application and API endpoints.
- `app/engine.py` – Core graph engine, state model, nodes, graphs, and run tracking.
- `app/tools.py` – Tool registry and simple Python functions used as node tools.
- `app/workflows.py` – Definition of the example workflow (code review mini-agent).
- `app/__init__.py` – Empty file so that `app` is recognized as a Python package.

This structure matches the requirement of having a FastAPI project in an `/app` folder and separates the engine logic, tools, and workflows for clarity.

## How to run

1. Go to the project root (where the `app` folder is located).

2. (Optional but recommended) Create and activate a virtual environment:
   - `python -m venv venv`
   - `venv\Scripts\activate` (on Windows)

3. Install dependencies:
   - `pip install fastapi uvicorn pydantic`

4. Start the FastAPI server from the project root:
   - `uvicorn app.main:app --reload`

5. Open the interactive API docs in your browser:
   - `http://127.0.0.1:8000/docs`

## How to use the APIs

From the `/docs` page you can call the endpoints in this order:

1. **Create example code review graph**

   Use `POST /graph/create_example/code_review`.

   - Click "Try it out" and then "Execute".
   - The response will return a `graph_id`.

2. **Run the graph**

   Use `POST /graph/run`.

   - Click "Try it out".
   - In the request body, provide the `graph_id` from the previous step and an `initial_state`. For example:

     ```
     {
       "graph_id": "PASTE_GRAPH_ID_HERE",
       "initial_state": {
         "code": "def foo():\n    print('hi')\n    # TODO: refactor\n",
         "threshold": 0.7
       }
     }
     ```

   - Click "Execute".
   - The response will return:
     - `run_id`
     - `final_state` (including quality score, suggestions, etc.)
     - `logs` (a list of node executions and state snapshots)

3. **Check run state (optional)**

   Use `GET /graph/state/{run_id}` with the `run_id` from the previous response if you want to inspect the saved run.

## What the workflow engine supports

- **Nodes**  
  Each node is represented by a Python function (tool) that reads and updates a shared state. Nodes are described by name, which tool they use, and which node should run next.

- **State**  
  The shared state is modeled with a Pydantic class. It flows from one node to another and can hold fields like `code`, `functions`, `complexity_score`, `issues`, `suggestions`, and `quality_score`.

- **Edges and execution order**  
  The engine stores a mapping of node names to `Node` definitions. Each node can specify a `next_node`, so the engine can move through the graph step by step.

- **Looping**  
  A node can define a simple loop condition. In this project, the quality node runs until the `quality_score` field in the state meets a threshold (or until a maximum loop count is hit to avoid infinite loops).

- **Branching (basic)**  
  The engine supports basic branching using a state field and a branch map. For this example workflow, the main focus is on the loop condition, but the engine can be extended with more complex branching logic.

- **Tool registry**  
  There is a simple registry that maps tool names to Python functions. This allows nodes to call different tools by name and keeps the engine generic and extensible.

## Example agent workflow (Code Review Mini-Agent)

The included example workflow implements the "Code Review Mini-Agent" described in the assignment. The steps are:

1. **Extract functions**  
   Scans the code and collects lines that look like function definitions into a `functions` list.

2. **Check complexity**  
   Uses a very simple heuristic based on the number of lines in the code to compute a `complexity_score`.

3. **Detect issues**  
   Counts simple patterns like `TODO` comments and `print(` calls as "issues".

4. **Suggest improvements**  
   Adds human-readable suggestions based on the complexity and number of issues.

5. **Compute quality and loop**  
   Computes a `quality_score` using rules derived from complexity and issues, and loops until `quality_score` is greater than or equal to a specified `threshold` or a maximum number of loops is reached.

This example shows how the engine can execute a realistic workflow with state, tools, and a loop condition.

## What I would improve with more time

If given more time, the following improvements would be considered:

- **Persistence layer**  
  Store graphs and runs in a real database (SQLite or Postgres) instead of in-memory dictionaries, so runs survive server restarts and can be queried later.

- **Richer branching and graph features**  
  Add more flexible branching based on numeric comparisons and multiple conditions, and allow more complex graph definitions via the API.

- **Async and long-running tasks**  
  Convert long-running tools to async functions, add background task handling, and possibly use a task queue for heavy workloads.

- **Better logging and observability**  
  Add structured logs, timestamps, and log levels for each node run, and expose logs via WebSocket for real-time monitoring.

- **Validation and error handling**  
  Add stricter validation for graph definitions and better error messages when a node or tool is misconfigured.

- **More workflows**  
  Implement the other example workflows from the assignment (summarization and data quality) to show versatility of the engine.
