from pyjokes import get_joke

from src.config import JOKE_LANGUAGES
from src.joke_state import JokeState, Joke

CHOICE_FETCH_JOKE = "fetch_joke"
CHOICE_UPDATE_CATEGORY = "update_category"
CHOICE_UPDATE_LANGUAGE = "update_language"
CHOICE_RESET_STATE = "reset_state"
CHOICE_EXIT_BOT = "exit_bot"
DECISION_APPROVED = "show_joke"
DECISION_REJECTED = "fetch_joke"

def get_user_input(prompt: str) -> str:
    return input(prompt).strip().lower()

def print_category_menu_header():
    """Print a nicely formatted category selection menu."""
    print("📂" + "=" * 58 + "📂")
    print("    CATEGORY SELECTION")
    print("=" * 60)

def print_joke(joke: Joke):
    """Print a joke with nice formatting."""
    # print(f"\n📂 CATEGORY: {joke.category.upper()}\n")
    print(f"\n😂 {joke.text}\n")
    print("=" * 60)



def route_choice(state: JokeState) -> str:
    match state.choice:
        case "n":
            return CHOICE_FETCH_JOKE
        case "c":
            return CHOICE_UPDATE_CATEGORY
        case "l":
            return CHOICE_UPDATE_LANGUAGE
        case "r":
            return CHOICE_RESET_STATE
        case "q":
            return CHOICE_EXIT_BOT
        case _:
            raise ValueError(f"Invalid choice: {state.choice}")

def update_language(_state: JokeState) -> dict:
    print("Available languages: ")
    for i, lang in enumerate(JOKE_LANGUAGES):
        print(f"    {i}. {lang.upper()}")
    try:
        choice = int(get_user_input("Select a language by number: "))
        while choice < 0 or choice >= len(JOKE_LANGUAGES):
             print("❌ Invalid choice. Please enter a valid number.")
             choice = int(get_user_input("Select a language by number: "))
        selected_language = JOKE_LANGUAGES[choice]
        print(f"✅ Language changed to {selected_language.upper()}")
        return {"language": selected_language}
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
        return {}

def fetch_joke(state: JokeState) -> dict:
    # Placeholder for joke fetching logic
    # In a real implementation, this would call an API or database
    joke = get_joke(language=state.language, category=state.category)
    new_joke = Joke(text=joke, category=state.category)
    print_joke(new_joke)
    return {"jokes": [new_joke]}  # LangGraph will use the add reducer to append this


def extract_joke_from_response(response: str) -> str:
    """
    Extract the actual joke from the LLM response.
    Removes preamble text like 'Here's a neutral developer joke:'
    and keeps only the first joke.
    """
    lines = response.split('\n')
    joke_lines = []

    for line in lines:
        line = line.strip()
        # Skip empty lines and preamble
        if not line or any(phrase in line.lower() for phrase in ["here's", "alternative", "or an"]):
            continue
        # Remove quotation marks if present
        line = line.strip('"')
        if line:
            joke_lines.append(line)
            # Stop after the first complete joke (usually 1-2 lines)
            if len(joke_lines) >= 2:
                break

    return ' '.join(joke_lines) if joke_lines else response

def exit_bot(_state: JokeState) -> dict:
    print("👋 Goodbye!")
    return {"quit": True}
