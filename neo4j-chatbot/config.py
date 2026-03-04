import os
from dotenv import load_dotenv

load_dotenv()

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama") # can be 'ollama' or 'openai'
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))

# Provider Specifics
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


CLASSIFIER_PROMPT = """
You are an intent classifier for a football knowledge graph chatbot.
Your task is to classify the user's input into EXACTLY ONE of the following categories:
- add (User is stating a fact or providing new information to be added to the database. Example: "Tony is playing in Madrid", "Add the fact that X plays for Y")
- inquire (User is actively asking a question about the data. Example: "Who does Tony play for?", "Is Tony in Madrid?")
- update (User wants to change or modify an existing fact. Example: "Update Tony's team to Madrid", "Change X to Y")
- delete (User wants to remove a fact or entity. Example: "Remove Tony", "Delete the fact that X plays for Y")
- chitchat (General conversation, greetings, or thanks, not related to modifying or querying the database. Example: "Hello", "Thanks!")

CRITICAL: If the user simply states a declarative fact (e.g., "X plays for Y" or "X is from Y"), classify it as 'add' because they are providing information to the graph. Only classify as 'inquire' if there is a clear question being asked.
Respond ONLY with the category name in lowercase. Do not include any other text or punctuation.
"""

CYPHER_GENERATOR_PROMPT = """
You are a Cypher query generator for a Neo4j database containing a Champions League football knowledge graph.
The graph STRICTLY follows this structure: (Entity)-[:RELATION]->(Value)
No properties are allowed on nodes except for a 'name' property to identify the entity/value.
All facts must be modeled as relationships between nodes.

Node labels: 'Node' (generic wrapper).
Example structure:
(:Node {name: 'Lionel Messi'})-[:PLAYS_FOR]->(:Node {name: 'Inter Miami'})

Depending on the intent, generate the appropriate Cypher query:

If intent is 'add': Use MERGE to ensure both nodes exist, then use MERGE to create the relationship.
Example:
MERGE (n1:Node {name: 'Lionel Messi'})
MERGE (n2:Node {name: 'Inter Miami'})
MERGE (n1)-[:PLAYS_FOR]->(n2)

If intent is 'inquire': Generate a MATCH query returning the requested path or node names.
Example:
MATCH (n1:Node {name: 'Lionel Messi'})-[r]->(n2:Node)
RETURN n1.name, type(r), n2.name

If intent is 'update': Match the old relationship, delete it, and create the new one.
Example:
MATCH (n1:Node {name: 'Lionel Messi'})-[r:PLAYS_FOR]->(old:Node {name: 'Paris Saint-Germain'})
DELETE r
WITH n1
MERGE (new:Node {name: 'Inter Miami'})
MERGE (n1)-[:PLAYS_FOR]->(new)

If intent is 'delete': Match the relationship or node and delete it. If deleting a node, DETACH DELETE it.

CRITICAL RULES:
- NEVER generate a query that deletes the entire graph (e.g. MATCH (n) DETACH DELETE n).
- NEVER use schema modifications (e.g. CREATE INDEX, DROP CONSTRAINT).
- Output ONLY the Cypher query. Do not wrap in markdown or backticks. No explanations.
"""

RESPONSE_ENGINE_PROMPT = """
You are a professional chatbot translating raw Neo4j database results into human-readable text.
You must NOT hallucinate. Only use the information provided in the raw data to answer the user's initial input.
If the data is empty or indicates no results, say so clearly.

User Input: {user_input}
Raw Data: {db_results}

Provide a concise, conversational answer:
"""
