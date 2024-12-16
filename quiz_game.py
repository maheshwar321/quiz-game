
import json
import random
import requests


QUESTIONS_FILE = "questions.json"
SCOREBOARD_FILE = "scoreboard.json"
API_URL = "https://opentdb.com/api.php?amount=10&type=multiple"

def load_questions(source='file', category=None, difficulty=None):
    """
    Load questions from a local file or an API.
    Supports filtering by category and difficulty.
    """
    if source == 'api':
        try:
            
            url = API_URL
            if category:
                url += f"&category={category}"
            if difficulty:
                url += f"&difficulty={difficulty.lower()}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            
            questions = []
            for item in data['results']:
                questions.append({
                    "text": item['question'],
                    "options": random.sample(item['incorrect_answers'] + [item['correct_answer']], k=4),
                    "correct": item['correct_answer'],
                    "category": item.get('category', 'General Knowledge'),
                    "difficulty": item.get('difficulty', 'Medium').capitalize()
                })
            return questions
        except requests.RequestException as e:
            print(f"Error fetching questions from API: {e}")
            return []

    elif source == 'file':
        try:
            with open(QUESTIONS_FILE, 'r') as file:
                questions = json.load(file)
                # Filter by category and difficulty
                filtered_questions = [
                    q for q in questions
                    if (category is None or q.get('category', '') == category) and
                       (difficulty is None or q.get('difficulty', '').lower() == difficulty.lower())
                ]
                return filtered_questions
        except FileNotFoundError:
            print("Questions file not found. Ensure 'questions.json' exists.")
            return []
    else:
        print("Invalid source specified.")
        return []

# Utility function to save scores
def save_score(username, score):
    try:
        with open(SCOREBOARD_FILE, 'r') as file:
            scoreboard = json.load(file)
    except FileNotFoundError:
        scoreboard = []

    scoreboard.append({"username": username, "score": score})
    with open(SCOREBOARD_FILE, 'w') as file:
        json.dump(scoreboard, file, indent=4)

# Function for player registration
def register_player():
    print("Welcome to the Quiz Game!")
    username = input("Enter your username: ").strip()
    return username

# Function to allow player to select difficulty and category
def select_quiz_preferences():
    print("\n--- Select Quiz Preferences ---")
    difficulty = input("Choose difficulty (Easy, Medium, Hard) or press Enter to skip: ").capitalize() or None
    category = input("Choose category (e.g., Science, History) or press Enter to skip: ").strip() or None
    return category, difficulty

# Function to play the quiz
def play_quiz(username, questions):
    if not questions:
        print("No questions available for the selected criteria. Try again!")
        return

    score = 0
    random.shuffle(questions)

    for i, question in enumerate(questions):
        print(f"\nQuestion {i + 1}: {question['text']}")
        for idx, option in enumerate(question['options'], start=1):
            print(f"{idx}. {option}")

        try:
            answer = int(input("Your answer (1-4): "))
            if question['options'][answer - 1] == question['correct']:
                print("Correct!")
                score += 1
            else:
                print(f"Wrong! The correct answer was: {question['correct']}")
        except (ValueError, IndexError):
            print("Invalid input. Skipping question.")

    print(f"\nQuiz finished! Your score: {score}/{len(questions)}")
    save_score(username, score)

# Main function
def main():
    # Register player
    username = register_player()

    # Choose question source (file or API)
    source = input("\nChoose question source (file or api): ").strip().lower()

    # Select category and difficulty
    category, difficulty = select_quiz_preferences()

    # Load questions
    questions = load_questions(source=source, category=category, difficulty=difficulty)

    # Play the quiz
    play_quiz(username, questions)

    # Show leaderboard
    print("\n--- Leaderboard ---")
    try:
        with open(SCOREBOARD_FILE, 'r') as file:
            scoreboard = json.load(file)
            for entry in sorted(scoreboard, key=lambda x: x['score'], reverse=True):
                print(f"{entry['username']}: {entry['score']}")
    except FileNotFoundError:
        print("No scores available yet.")

# Entry point
if __name__ == "__main__":
    main()
