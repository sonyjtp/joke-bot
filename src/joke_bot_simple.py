"""
A simple joke-telling chatbot implemented using LangGraph, without any LLMs.
This example demonstrates how to build an agentic state flow using LangGraph, where the bot can fetch jokes,
change categories, and keep track of the jokes it has told. The bot uses the `pyjokes` library to fetch jokes based on
user-selected categories and languages.
"""

from typing import get_args

from langchain_core.runnables import RunnableConfig
from langgraph.constants import END
from langgraph.graph import StateGraph
from pyjokes import get_joke

from src.joke_state import CHOICES, JokeState, Joke
from src.utils.joke_helper import get_user_input_in_lowercase, update_language, exit_bot, print_category_menu_header, fetch_joke, \
    route_choice


def print_menu_header(category: str, total_jokes: int):
    """Print a compact menu header."""
    print(f"🎭 Menu | Category: {category.upper()} | Jokes: {total_jokes}")
    print("-" * 50)


# Nodes

def show_menu(state: JokeState) -> dict:
    print_menu_header(state.category, len(state.jokes))
    print("[n] 🎭 Next Joke  [c] 📂 Change Category [l] 🌐 Change Language [r] 🔄 Reset  [q] ❌ Quit")
    choice = get_user_input_in_lowercase("Your choice: ")
    while choice not in get_args(CHOICES):
        print("❌ Invalid choice. Please enter 'n', 'c', 'l', r' or 'q'.")
        choice = get_user_input_in_lowercase("Your choice: ")
    return {"jokes_choice": choice}

def update_category(state: JokeState) -> dict:
    categories = ["neutral", "chuck", "all"]
    print_category_menu_header()
    print("Available categories: ")
    for i, cat in enumerate(categories):
        emoji = "🎯" if cat == "neutral" else "🥋" if cat == "chuck" else "🌟"
        print(f"    {i}. {emoji} {cat.upper()}")
    try:
        choice = int(get_user_input_in_lowercase("Select a category by number: "))
        if choice < 0 or choice >= len(categories):
            print("❌ Invalid choice. Please enter a valid number.")
            return {}
        selected_category = categories[choice]
        print(f"✅ Category changed to {selected_category.upper()}")
        return {"category": selected_category}
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
        return {}

def reset_state(state: JokeState) -> dict:
    print("🔄 Resetting joke history and settings to defaults.")
    return {
        "jokes": [],  # Clear joke history
        "category": "neutral",  # Reset category
        "language": "en",  # Reset language
        "jokes_choice": "n"  # Reset choice to next joke
    }


# Build graph

def build_joke_bot_graph():
    workflow = StateGraph(state_schema=JokeState)

    # register nodes
    workflow.add_node("show_menu", show_menu)
    workflow.add_node("fetch_joke", fetch_joke)
    workflow.add_node("update_category", update_category)
    workflow.add_node("update_language", update_language)
    workflow.add_node("reset_state", reset_state)
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
            "update_language": "update_language",
            "reset_state": "reset_state",
            "exit_bot": "exit_bot",
        }
    )

    # define transitions after fetch and update
    workflow.add_edge("fetch_joke", "show_menu")
    workflow.add_edge("update_category", "show_menu")
    workflow.add_edge("update_language", "show_menu")
    workflow.add_edge("reset_state", "show_menu")
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
    for idx, joke in enumerate(JokeState(**final_state).jokes, 1):
        print(f"{idx}. [{joke.category.upper()}] {joke.text}")



# # Main execution
if __name__ == "__main__":
    main()


