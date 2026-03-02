# Inventory Chatbot

A minimal AI chat service designed to answer inventory and business questions from a database. It generates SQL queries locally using LangGraph and Mistral (via Ollama) or OpenAI models.

## 🏗️ System Architecture

### 1. Overall Application Flow

```mermaid
sequenceDiagram
    participant User
    participant Streamlit (UI)
    participant FastAPI (API)
    participant LangGraph (Agent)
    participant LLM (Ollama/OpenAI)
    participant SQLite (DB)

    User->>Streamlit (UI): Asks question
    Streamlit (UI)->>FastAPI (API): POST /api/chat
    FastAPI (API)->>LangGraph (Agent): Invoke Agent
    LangGraph (Agent)->>LLM (Ollama/OpenAI): Generate/Fix SQL
    LLM (Ollama/OpenAI)-->>LangGraph (Agent): SQL Query
    LangGraph (Agent)->>SQLite (DB): Execute Query
    SQLite (DB)-->>LangGraph (Agent): Data Results
    LangGraph (Agent)->>LLM (Ollama/OpenAI): Format Answer
    LLM (Ollama/OpenAI)-->>LangGraph (Agent): Natural Language Answer
    LangGraph (Agent)-->>FastAPI (API): Final State
    FastAPI (API)-->>Streamlit (UI): JSON Response
    Streamlit (UI)-->>User: Answers + SQL + Metrics
```

### 2. LangGraph Workflow

```mermaid
graph TD
    Start((Start)) --> Router{Router Node}
    Router -->|chat| Chat[Chat Node]
    Router -->|sql| SQLGen[SQL Generator]

    SQLGen --> SQLExec[SQL Executor]
    SQLExec --> Check{Error?}

    Check -->|Yes| SQLCorr[SQL Corrector]
    SQLCorr --> SQLExec

    Check -->|No| Resp[Responder Node]
    Chat --> Resp
    Resp --> End((End))

    subgraph "Self-Correction Loop"
    SQLExec
    Check
    SQLCorr
    end
```

## 🚀 Setup & Installation

### 1. Prerequisites

- Python 3.10+
- **Ollama** (if using local Mistral)
- **OpenAI API Key** (if using OpenAI)

### 2. Environment Setup

Create a virtual environment outside the folder:

```powershell
python -m venv ../venv
../venv/Scripts/Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

### 3. Database Initialization

Ensure the local SQLite database is created and seeded:

```powershell
python setup_database.py
```

### 4. Configuration (.env)

Create a `.env` file in the `inventory-chatbot` folder:

```env
# PROVIDER options: 'ollama' or 'openai'
PROVIDER=ollama
MODEL_NAME=mistral

# If using OpenAI:
# PROVIDER=openai
# MODEL_NAME=gpt-4o
# OPENAI_API_KEY=your_key_here
```

## 🏃 Running the Project

1. **Start the API Server**:

```powershell
python api.py
```

2. **Start the UI (Streamlit)**:

```powershell
python -m streamlit run app.py
```

## 🛠️ Project Structure

- `api.py`: FastAPI server handling the chat endpoint.
- `app.py`: Streamlit UI for interaction and debugging.
- `agent/`:
  - `graph.py`: LangGraph workflow definition.
  - `nodes.py`: Logic for each agent node.
  - `prompts.py`: System prompts and schema handling.
  - `state.py`: Definition of the agent's state.
- `schema.sql`: Database DDL (Source of truth).
- `inventory_chatbot.db`: Local SQLite database.
