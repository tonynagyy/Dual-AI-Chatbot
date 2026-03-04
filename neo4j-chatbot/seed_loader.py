import os
from classifier import IntentClassifier
from cypher_generator import CypherGenerator
from executor import Neo4jExecutor

def load_seed_data(file_path: str = "seed_data.txt"):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    classifier = IntentClassifier()
    generator = CypherGenerator()
    executor = Neo4jExecutor()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        print(f"Starting seed loading for {len(lines)} facts...\\n")

        for line in lines:
            print(f"Inserting: {line}")
            
            intent = classifier.classify(line)
            if intent != "add":
                intent = "add"

            try:
                cypher_query = generator.generate(line, intent)
                
                executor.execute_query(cypher_query)
                
                print("Success.")
            except Exception as e:
                print(f"Failed. Error: {e}")
                
            print("-" * 40)
            
    finally:
        executor.close()
        print("Seed loading complete.")

if __name__ == "__main__":
    load_seed_data()
