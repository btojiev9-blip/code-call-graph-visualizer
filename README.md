# Code Call Graph Visualizer

## description
A lightweight FastAPI backend project built with Clean Architecture that parses Python source code and generates Mermaid.js call graphs.

## concept
1. Minimal functionality.
2. Convincing architecture (Clean Architecture layers).
3. Easy to read and review.
4. Database history tracking.

## architecture layers
1. **app/domain**: Pure business logic (AST code parser).
2. **app/infrastructure**: Database connection and models (SQLite & SQLAlchemy).
3. **app/api**: Request schemas (Pydantic) and endpoints (FastAPI routers).

## integrated with
1. Python 3.10+
2. FastAPI
3. Database
   1. SQLite (local file database)
   2. SQLAlchemy (ORM framework)

## commands
1. **Installation**
   1. `pip install -r requirements.txt`: install all required packages
2. **Server**
   1. `uvicorn main:app --reload`: start local development server
   2. Open interactive docs: `http://127.0.0.1:8000/docs`

## sample env / requests
**POST** `/api/analyze`
```json
{
  "code": "def start():\n    step_one()"
}
