import sys
import logging
from classifier import IntentClassifier
from cypher_generator import CypherGenerator
from executor import Neo4jExecutor
from response_engine import ResponseEngine

logging.getLogger("config").setLevel(logging.WARNING)
logging.getLogger("executor").setLevel(logging.WARNING)
logging.getLogger("classifier").setLevel(logging.WARNING)
logging.getLogger("cypher_generator").setLevel(logging.WARNING)
logging.getLogger("response_engine").setLevel(logging.WARNING)

class ChatbotOrchestrator:
    def __init__(self):
        print("Initializing NLP models and Database connection...")
        try:
            self.classifier = IntentClassifier()
            self.generator = CypherGenerator()
            self.executor = Neo4jExecutor()
            self.responder = ResponseEngine()
            
            self.memory = []
            
            print("Chatbot successfully initialized!")
            print("=" * 50)
            print("Welcome to the Champions League Knowledge Graph Bot")
            print("Type 'exit' or 'quit' to close the application.")
            print("=" * 50)
        except Exception as e:
            print(f"Fatal error during initialization: {e}")
            sys.exit(1)

    def process_input(self, user_input: str):

        try:
            intent = self.classifier.classify(user_input)
            
            if intent == "chitchat":
                response = self.responder.generate_chitchat(user_input)
                print(f"\\nBot: {response}\\n")
                return

            cypher_query = self.generator.generate(user_input, intent)
            
            raw_results = self.executor.execute_query(cypher_query)
            
            if intent in ["add", "update", "delete"]:
                action_map = {"add": "added", "update": "updated", "delete": "removed"}
                print(f"\\nBot: Successfully executed Cypher query. Fact {action_map.get(intent, 'modified')}.\\n")
            else:
                response = self.responder.generate_response(user_input, raw_results)
                print(f"\\nBot: {response}\\n")
            
            self.memory.append(user_input)
            if len(self.memory) > 5:
                self.memory.pop(0)

        except Exception as e:
            print(f"\\nBot: I'm sorry, I encountered an error processing your request: {e}\\n")

    def run(self):
        while True:
            try:
                user_input = input("User: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("Goodbye!")
                    break

                self.process_input(user_input)

            except KeyboardInterrupt:
                print("\\nGoodbye!")
                break
            except Exception as e:
                print(f"\\nAn unexpected error occurred: {e}")

        try:
            self.executor.close()
        except:
            pass

if __name__ == "__main__":
    app = ChatbotOrchestrator()
    app.run()
