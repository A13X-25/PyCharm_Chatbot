import json
from difflib import get_close_matches
from datetime import datetime


class LearningChatBot:
    def __init__(self, knowledge_base_path: str):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = self.load_knowledge_base()
        self.conversation_history = []

    def load_knowledge_base(self) -> dict:
        try:
            with open(self.knowledge_base_path, 'r') as file:
                data: dict = json.load(file)
            return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return {
                "questions": [],
                "synonyms": {},
                "interaction_stats": {}
            }

    def save_knowledge_base(self):
        try:
            with open(self.knowledge_base_path, 'w') as file:
                json.dump(self.knowledge_base, file, indent=2)
        except IOError as e:
            print(f"Error saving knowledge base: {e}")

    def find_best_match(self, user_question: str) -> tuple[str | None, float]:
        questions = [q["question"] for q in self.knowledge_base["questions"]]
        matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)

        if matches:
            similarity = self.calculate_similarity(user_question, matches[0])
            return matches[0], similarity
        return None, 0.0

    def calculate_similarity(self, str1: str, str2: str) -> float:
        # Simple word overlap similarity
        words1 = set(str1.lower().split())
        words2 = set(str2.lower().split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0

    def update_interaction_stats(self, question: str, was_helpful: bool):
        stats = self.knowledge_base.get("interaction_stats", {})
        if question not in stats:
            stats[question] = {"helpful": 0, "not_helpful": 0, "last_used": None}

        stats[question]["last_used"] = datetime.now().isoformat()
        if was_helpful:
            stats[question]["helpful"] += 1
        else:
            stats[question]["not_helpful"] += 1

        self.knowledge_base["interaction_stats"] = stats
        self.save_knowledge_base()

    def learn_new_response(self, question: str, answer: str):
        self.knowledge_base["questions"].append({
            "question": question,
            "answer": answer,
            "created_at": datetime.now().isoformat(),
            "times_used": 0
        })
        self.save_knowledge_base()

    def get_answer(self, question: str) -> str | None:
        for q in self.knowledge_base["questions"]:
            if q["question"] == question:
                q["times_used"] = q.get("times_used", 0) + 1
                self.save_knowledge_base()
                return q["answer"]
        return None

    def chat(self):
        print("Bot: Hello! I'm a learning chatbot. I can learn from our conversations!")
        print("Bot: Type 'exit' to end the conversation, or 'help' for commands.")

        while True:
            user_input: str = input("You: ").strip()

            if not user_input:
                print("Bot: Please enter a valid question.")
                continue

            if user_input.lower() == "exit":
                print("Bot: Goodbye! Thanks for chatting!")
                break

            if user_input.lower() == "help":
                print("\nAvailable commands:")
                print("- 'exit': End the conversation")
                print("- 'help': Show this help message")
                print("- 'feedback': Give feedback on the last response")
                continue

            best_match, similarity = self.find_best_match(user_input)

            if best_match and similarity > 0.6:
                answer = self.get_answer(best_match)
                print(f'Bot: {answer}')

                feedback = input("Was this response helpful? (yes/no): ").lower()
                self.update_interaction_stats(best_match, feedback == "yes")

                if feedback == "no":
                    new_answer = input("Would you like to provide a better answer? (Enter answer or 'skip'): ").strip()
                    if new_answer.lower() != "skip":
                        self.learn_new_response(user_input, new_answer)
                        print("Bot: Thank you! I've learned from your feedback!")
            else:
                print("Bot: I don't know how to respond to that yet. Would you like to teach me?")
                new_answer = input("Enter an appropriate response or 'skip': ").strip()

                if new_answer.lower() != "skip":
                    self.learn_new_response(user_input, new_answer)
                    print("Bot: Thank you! I've learned something new!")


if __name__ == '__main__':
    chatbot = LearningChatBot('knowledge_base.json')
    chatbot.chat()
