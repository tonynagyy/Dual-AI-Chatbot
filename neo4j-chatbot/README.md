# Neo4j AI Chatbot (Champions League Football)

A terminal-based AI chatbot that uses the Ollama "mistral" model to answer questions and interact with a Champions League Football Knowledge Graph stored in Neo4j. The architecture follows strict clean architecture and separation of concerns.

## Prerequisites & Setup

### 1. Python Virtual Environment

First, ensure you have Python 3.9+ installed. Create a virtual environment:

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

Install the required packages using `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration (.env)

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Open `.env` and set your variables. You can choose between `ollama` or `openai` as your `LLM_PROVIDER`. If you use OpenAI, be sure to provide your `OPENAI_API_KEY`.

### 5. Install & Setup Subsystems

**If using Ollama:**

- Download Ollama from: [https://ollama.com/download](https://ollama.com/download)
- Pull the model: `ollama run mistral`

**If using Neo4j:**

- Download Neo4j Desktop from: [https://neo4j.com/download/](https://neo4j.com/download/)
- Create a local DBMS, set the password (update `.env` if different from `password`), and start it. Ensure it's reachable at `bolt://localhost:7687`.

### 7. Create and Start DB

- Open Neo4j Desktop and create a new project.
- Click "Add" -> "Local DBMS". Name it appropriately and set the password to `password` (or update `config.py` with your custom password).
- Click "Start" on the DBMS.
- Ensure the connection is available at `bolt://localhost:7687`.

### 8. Run the Seed Loader

With Neo4j running, populate the knowledge graph with initial facts:

```bash
python seed_loader.py
```

This will insert 50 lines of Champions League football facts into Neo4j.

### 9. Run the Chatbot

Start the interactive terminal application:

```bash
python main.py
```

## Example Interactions

**Inquire:**

> User: Who does Lionel Messi play for?
> Bot: Based on the knowledge graph, Lionel Messi plays for Inter Miami.

**Add:**

> User: Add the fact that Cody Gakpo plays for Liverpool.
> Bot: Successfully executed Cypher query. Fact added.

**Update:**

> User: Update the fact that Kylian Mbappé plays for Real Madrid to Paris Saint-Germain.
> Bot: Successfully executed Cypher query. Fact updated.

**Delete:**

> User: Remove the fact that Kevin De Bruyne plays for Manchester City.
> Bot: Successfully executed Cypher query. Fact removed.

**Chitchat:**

> User: Hello!
> Bot: Hello! How can I help you with Champions League football knowledge today?
