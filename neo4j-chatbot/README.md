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

Open `.env` and configure the variables based on your preferred LLM provider:

| Provider   | `LLM_PROVIDER` | Extra Variable(s) | Notes                     |
| :--------- | :------------- | :---------------- | :------------------------ |
| **Ollama** | `ollama`       | `OLLAMA_URL`      | Local, free, offline      |
| **OpenAI** | `openai`       | `OPENAI_API_KEY`  | High quality, paid        |
| **Groq**   | `groq`         | `GROQ_API_KEY`    | Extremely fast, free tier |

---

## Subsystem Setup

### 1. LLM Provider Setup

#### **Option A: Ollama (Local)**

1. Download from [ollama.com](https://ollama.com/download).
2. Install and run the application.
3. Pull the model:
   ```bash
   ollama run mistral
   ```
4. Set `.env`: `LLM_PROVIDER=ollama`, `LLM_MODEL=mistral`.

#### **Option B: Groq (Cloud)**

1. Get a free API key at [groq.com](https://groq.com/).
2. Set `.env`: `LLM_PROVIDER=groq`, `GROQ_API_KEY=gsk_...`
3. Suggested Model: `llama-3.3-70b-versatile` or `llama-3.1-8b-instant`.

#### **Option C: OpenAI (Cloud)**

1. Get an API key from [platform.openai.com](https://platform.openai.com/).
2. Set `.env`: `LLM_PROVIDER=openai`, `OPENAI_API_KEY=sk-...`
3. Suggested Model: `gpt-4o` or `gpt-3.5-turbo`.

---

### 2. Neo4j Database Setup

1. **Download Neo4j Desktop**: [neo4j.com/download](https://neo4j.com/download/).
2. **Create a Local DBMS**:
   - Open Neo4j Desktop and create a new project.
   - Click **Add** -> **Local DBMS**.
   - Set the name (e.g., "Football-Graph") and password (default is `password`).
3. **Start the DBMS**: Click the **Start** button.
4. **Connection Check**: Ensure it is reachable at `bolt://localhost:7687`.
5. **Update .env**: Ensure `NEO4J_PASSWORD` matches what you set.

### 3. Viewing the Database Visually (Neo4j Browser)

To view the graph and verify your data visually as nodes and edges:

1. Open your web browser and navigate to **http://localhost:7474**.
2. Log in using the credentials from your `.env` file (by default, Username: `neo4j`, Password: `<your_password>`).
3. In the query bar at the top, enter the following Cypher query and press Enter (or click Play) to view all nodes and connections:
   ```cypher
   MATCH (n) RETURN n
   ```
4. You can click on individual nodes to explore their properties (e.g., names, stats) or test more specific Cypher queries, such as seeing who plays for Real Madrid:
   ```cypher
   MATCH (p:Person)-[r:PLAYS_FOR]->(t:Team {name: "Real Madrid"}) RETURN p, r, t
   ```

### 4. Run the Seed Loader

With Neo4j running, populate the knowledge graph with initial facts:

```bash
python seed_loader.py
```

This will insert 50 lines of Champions League football facts into Neo4j.

### 5. Run the Chatbot

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
