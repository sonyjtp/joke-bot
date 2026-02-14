"""
A simple joke-telling chatbot implemented using LangGraph, without any LLMs.
This example demonstrates how to build an agentic state flow using LangGraph, where the bot can fetch jokes,
change categories, and keep track of the jokes it has told. The bot uses the `pyjokes` library to fetch jokes based on
user-selected categories and languages.
"""

from operator import add
from typing import Annotated, Literal

from langchain_core.runnables import RunnableConfig
from langgraph.constants import END
from langgraph.graph import StateGraph
from pydantic import BaseModel
from pyjokes import get_joke
from pyjokes.pyjokes import LANGUAGES, CATEGORIES


class Joke(BaseModel):
    text: str
    category: str

class JokeState(BaseModel):
    jokes: Annotated[list[Joke], add] = []  # Using built-in add operator
    jokes_choice: Literal["n", "c", "q"] = "n" # next, change, quit
    category: CATEGORIES = "neutral"
    language: LANGUAGES = "en"
    quit: bool = False

def get_user_input(prompt: str) -> str:
    return input(prompt).strip().lower()

def print_joke(joke: Joke):
    """Print a joke with nice formatting."""
    # print(f"\n📂 CATEGORY: {joke.category.upper()}\n")
    print(f"\n😂 {joke.text}\n")
    print("=" * 60)

def print_menu_header(category: str, total_jokes: int):
    """Print a compact menu header."""
    print(f"🎭 Menu | Category: {category.upper()} | Jokes: {total_jokes}")
    print("-" * 50)

def print_category_menu():
    """Print a nicely formatted category selection menu."""
    print("📂" + "=" * 58 + "📂")
    print("    CATEGORY SELECTION")
    print("=" * 50)


# Nodes

def show_menu(state: JokeState) -> dict:
    print_menu_header(state.category, len(state.jokes))
    print("[n] 🎭 Next Joke  [c] 📂 Change Category  [q] 🚪 Quit")
    choice = get_user_input("Your choice: ")
    while choice not in ["n", "c", "q"]:
        print("❌ Invalid choice. Please enter 'n', 'c', or 'q'.")
        choice = get_user_input("Your choice: ")
    return {"jokes_choice": choice}

def fetch_joke(state: JokeState) -> dict:
    # Placeholder for joke fetching logic
    # In a real implementation, this would call an API or database
    joke = get_joke(language=state.language, category=state.category)
    new_joke = Joke(text=joke, category=state.category)
    print_joke(new_joke)
    return {"jokes": [new_joke]}  # LangGraph will use the add reducer to append this

def update_category(state: JokeState) -> dict:
    categories = ["neutral", "chuck", "all"]
    print_category_menu()
    print("Available categories: ")
    for i, cat in enumerate(categories):
        emoji = "🎯" if cat == "neutral" else "🥋" if cat == "chuck" else "🌟"
        print(f"    {i}. {emoji} {cat.upper()}")
    try:
        choice = int(get_user_input("Select a category by number: "))
        if choice < 0 or choice >= len(categories):
            print("❌ Invalid choice. Please enter a valid number.")
            return {}
        selected_category = categories[choice]
        print(f"✅ Category changed to {selected_category.upper()}")
        return {"category": selected_category}
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
        return {}

def exit_bot(state: JokeState) -> dict:
    print("👋 Goodbye!")
    return {"quit": True}

def route_choice(state: JokeState) -> str:
    if state.jokes_choice == "n":
        return "fetch_joke"
    elif state.jokes_choice == "c":
        return "update_category"
    elif state.jokes_choice == "q":
        return "exit_bot"
    else:
        print("❌ Invalid choice. This should never happen.")
        return ""

# Build graph

def build_joke_bot_graph():
    workflow = StateGraph(state_schema=JokeState)

    # register nodes
    workflow.add_node("show_menu", show_menu)
    workflow.add_node("fetch_joke", fetch_joke)
    workflow.add_node("update_category", update_category)
    workflow.add_node("exit_bot", exit_bot)

    # set entry point
    workflow.set_entry_point("show_menu")

    # add conditional edges based on user choice
    workflow.add_conditional_edges(
        source="show_menu",
        path=route_choice,
        path_map={
            "fetch_joke": "fetch_joke",
            "update_category": "update_category",
            "exit_bot": "exit_bot",
        }
    )

    # define transitions after fetch and update
    workflow.add_edge("fetch_joke", "show_menu")
    workflow.add_edge("update_category", "show_menu")
    workflow.add_edge("exit_bot", END)

    return workflow.compile()

def main():
    print("🤖 Welcome to the Joke Bot!")
    print("This example demonstrates a joke-telling chatbot using LangGraph, but without LLMs.")
    print("Type 'q' at any time to quit.\n")

    graph = build_joke_bot_graph()

    print(" Starting Joke Bot Session...\n")

    final_state = graph.invoke(
        input=JokeState(),
        config=RunnableConfig(recursion_limit=100)  # Prevent infinite loops
    )

    print("\nJoke Bot Session Ended. Here are all the jokes you received:")
    for idx, joke in enumerate(final_state.jokes, 1):
        print(f"{idx}. [{joke.category.upper()}] {joke.text}")



# # Main execution
if __name__ == "__main__":
    main()


