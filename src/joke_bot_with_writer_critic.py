from typing import get_args

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from chat_model import WriterModel
from config import PROMPT_CONFIG_FILE_NAME
from joke_state import CHOICES, AgenticJokeState, Joke
from llm_utils import get_llm
from prompt_builder import build_prompt_from_config
from utils.file_utils import load_yaml
from utils.joke_helper import update_language, get_user_input_in_lowercase, print_category_menu_header, exit_bot, route_choice, \
    CHOICE_FETCH_JOKE, CHOICE_UPDATE_CATEGORY, CHOICE_UPDATE_LANGUAGE, CHOICE_RESET_STATE, CHOICE_VIEW_CATALOG, CHOICE_EXIT_BOT, \
    DECISION_APPROVED, DECISION_REJECTED, extract_joke_from_response
from utils.joke_catalog import save_joke_to_catalog, display_catalog_stats, view_catalog_by_category

load_dotenv()

NODE_SHOW_MENU = "show_menu"
NODE_UPDATE_CATEGORY = "update_category"
NODE_UPDATE_LANGUAGE = "update_language"
NODE_WRITER = "writer"
NODE_CRITIC = "critic"
NODE_CHECK_JOKE_REPETITION = "check_repetition"
NODE_RESET_STATE = "reset_state"
NODE_SHOW_JOKE = "show_joke"
NODE_VIEW_CATALOG = "view_catalog"
NODE_EXIT_BOT = "exit_bot"


def build_graph() -> CompiledStateGraph:
    graph = StateGraph(state_schema=AgenticJokeState)
    add_nodes(graph)
    graph.set_entry_point(NODE_SHOW_MENU)
    add_conditional_edges(graph)
    add_edges(graph)
    return graph.compile()


def add_nodes(graph: StateGraph):
    graph.add_node(node=NODE_SHOW_MENU, action=show_menu)
    graph.add_node(node=NODE_UPDATE_CATEGORY, action=update_category)
    graph.add_node(node=NODE_UPDATE_LANGUAGE, action=update_language)
    graph.add_node(node=NODE_WRITER, action=create_writer(get_llm(writer_model)))
    graph.add_node(node=NODE_CRITIC, action=request_for_human_approval)
    graph.add_node(node=NODE_CHECK_JOKE_REPETITION, action=check_repetition)
    graph.add_node(node=NODE_RESET_STATE, action=reset_state)
    graph.add_node(node=NODE_SHOW_JOKE, action=show_joke)
    graph.add_node(node=NODE_VIEW_CATALOG, action=view_catalog)
    graph.add_node(node=NODE_EXIT_BOT, action=exit_bot)


def add_conditional_edges(graph: StateGraph):
    graph.add_conditional_edges(
        source=NODE_SHOW_MENU,
        path=route_choice,
        path_map={
            # choice: next_node
            CHOICE_FETCH_JOKE: NODE_WRITER,
            CHOICE_UPDATE_CATEGORY: NODE_UPDATE_CATEGORY,
            CHOICE_UPDATE_LANGUAGE: NODE_UPDATE_LANGUAGE,
            CHOICE_RESET_STATE: NODE_RESET_STATE,
            CHOICE_VIEW_CATALOG: NODE_VIEW_CATALOG,
            CHOICE_EXIT_BOT: NODE_EXIT_BOT,
        }
    )
    graph.add_conditional_edges(
        source=NODE_CRITIC,
        path=route_critic_decision,
        path_map={
            # decision: next_node
            DECISION_REJECTED: NODE_WRITER,
            DECISION_APPROVED: NODE_SHOW_JOKE
        }
    )

    graph.add_conditional_edges(
        source=NODE_CHECK_JOKE_REPETITION,
        path=route_repetition_decision,
        path_map={
            DECISION_APPROVED: NODE_CRITIC,
            DECISION_REJECTED: NODE_WRITER
        }
    )

def add_edges(graph: StateGraph):
    graph.add_edge(start_key=NODE_UPDATE_CATEGORY, end_key=NODE_SHOW_MENU)
    graph.add_edge(start_key=NODE_UPDATE_LANGUAGE, end_key=NODE_SHOW_MENU)
    graph.add_edge(start_key=NODE_WRITER, end_key=NODE_CHECK_JOKE_REPETITION)
    graph.add_edge(start_key=NODE_SHOW_JOKE, end_key=NODE_SHOW_MENU)
    graph.add_edge(start_key=NODE_VIEW_CATALOG, end_key=NODE_SHOW_MENU)
    graph.add_edge(start_key=NODE_EXIT_BOT, end_key=END)

def show_menu(state: AgenticJokeState) -> dict:
    print(f"🎭 Menu | Category: {state.category.upper()} | Jokes: {len(state.jokes)}")
    print("[n] 🎭 Next Joke  [c] 📂 Change Category [l] 🌐 Change Language [b] 📚 Browse Catalog [r] 🔄 Reset  [q] ❌ Quit")
    choice = get_user_input_in_lowercase("Your choice: ").lower()
    while choice not in get_args(CHOICES):
        print(f"❌ Invalid choice. Please enter one of {', '.join(get_args(CHOICES))}.")
        choice = get_user_input_in_lowercase("Your choice: ").lower()
    return {"choice": choice}

def update_category(_state: AgenticJokeState) -> dict:
    categories = ["neutral", "chuck", "all"]
    print_category_menu_header()
    print_category_menu(categories)

    try:
        selection = int(input("    Enter category number: ").strip())
        while selection < 0 or selection >= len(categories):
            print("    ❌ Invalid choice. Please enter a number corresponding to the categories listed.")
            selection = int(input("    Enter category number: ").strip())
        selected_category = categories[selection]
        print(f"    ✅ Category changed to: {selected_category.upper()}")
        return {"category": selected_category}
    except ValueError:
        print("    ❌ Invalid number. Keeping current category.")
        return {}

def create_writer(writer_llm):
    def writer_node(state: AgenticJokeState) -> dict:
        prompt = build_prompt_from_config(
            config=prompt_config["joke_writer_cfg"],
            input_data="",
            app_config=None
        )
        prompt += f"\nThe category is: {state.category}"
        response = writer_llm.invoke(prompt)
        joke_text = extract_joke_from_response(response.content.strip())
        print(f"\n✍️  Writer generated a joke: {joke_text}\n")
        return {"latest_joke": joke_text}
    return writer_node

# def create_critic(critic_llm):
#     def critic_node(state: AgenticJokeState) -> dict:
#         prompt = build_prompt_from_config(
#             config=prompt_config["joke_critic_cfg"],
#             input_data=state.latest_joke,
#             app_config=None
#         )
#         decision = critic_llm.invoke(prompt).content.strip().lower()
#         approved = "yes" in decision
#         if not approved:
#             print("❌ Critic rejected the joke. Fetching a new one...")
#         return {"approved": approved, "retry_count": state.retry_count + 1}
#     return critic_node

def request_for_human_approval(state: AgenticJokeState) -> dict:
    """Ask human to approve the generated joke."""
    print(f"😂 {state.latest_joke}\n")
    while True:
        approval = get_user_input_in_lowercase("Do you like this joke? (y/n): ").lower()
        if approval in ["y", "yes"]:
            print("✅ Joke approved!")
            return {"approved": True, "retry_count": state.retry_count + 1}
        elif approval in ["n", "no"]:
            print("❌ Joke rejected. Fetching a new one...")
            return {"approved": False, "retry_count": state.retry_count + 1}
        else:
            print("❌ Invalid input. Please enter 'y' or 'n'.")

def check_repetition(state: AgenticJokeState) -> dict:
    if any(joke.text == state.latest_joke for joke in state.jokes):
        print("⚠️  This joke has already been told. Fetching a new one...")
        return {"repetition": True, "retry_count": state.retry_count + 1}
    return {"repetition": False}

def reset_state(_state: AgenticJokeState) -> dict:
    print("🔄 State has been reset to initial values.")
    return {
        "category": "neutral",
        "language": "en",
        "jokes": [],
        "latest_joke": "",
        "approved": False,
        "retry_count": 0,
    }

def view_catalog(_state: AgenticJokeState) -> dict:
    """Display catalog statistics and browse jokes."""
    display_catalog_stats()

    # Ask user if they want to browse by category
    category_choice = get_user_input_in_lowercase("Browse jokes by category? (y/n): ").lower()
    if category_choice in ["y", "yes"]:
        categories = ["neutral", "chuck", "all"]
        print_category_menu_header()
        print_category_menu(categories)
        try:
            selection = int(input("    Enter category number: ").strip())
            while selection < 0 or selection >= len(categories):
                print("    ❌ Invalid choice. Please enter a number corresponding to the categories listed.")
                selection = int(input("    Enter category number: ").strip())
            selected_category = categories[selection]
            jokes = view_catalog_by_category(selected_category)
            if jokes:
                print(f"\n📚 Jokes in '{selected_category.upper()}' category:")
                print("=" * 60)
                for i, joke in enumerate(jokes, 1):
                    print(f"{i}. {joke['text']}")
                    print("-" * 60)
            else:
                print(f"❌ No jokes found in '{selected_category.upper()}' category.")
        except ValueError:
            print("    ❌ Invalid number. Returning to menu.")

    return {}

def show_joke(state: AgenticJokeState) -> dict:
    joke = Joke(text=state.latest_joke, category=state.category)
    print_joke(joke)

    # Persist approved joke to catalog
    save_joke_to_catalog(joke)

    return {
        "jokes": [joke.model_dump()],  # model_dump to convert Joke object to dict for state storage
        "retry_count": 0,
        "approved": False,
        "latest_joke": ""
    }


def route_critic_decision(state: AgenticJokeState) -> str:
    if state.approved or state.retry_count >= 5:
        return DECISION_APPROVED
    return DECISION_REJECTED


def route_repetition_decision(state: AgenticJokeState) -> str:
    if state.repetition:
        return DECISION_REJECTED
    else:
        return DECISION_APPROVED


def print_category_menu(categories: list[str]):
    emoji_map = {
        "neutral": "😐",
        "chuck": "🥋",
        "all": "🎯",
    }
    for i, cat in enumerate(categories):
        emoji = emoji_map.get(cat, "📂")
        print(f" {i}. {emoji} {cat.upper()}")

    print("=" * 60)

def print_joke(joke: Joke):
    """Print a joke with nice formatting."""
    # print(f"\n📂 CATEGORY: {joke.category.upper()}\n")
    print(f"\n😂 {joke.text}\n")
    print("=" * 60)

def main():
    compiled_graph = build_graph()
    final_state = compiled_graph.invoke(
        input=AgenticJokeState(),
        config=RunnableConfig(recursion_limit=200)
    )
    print("\n✅ Session complete! Joke count:".format(len(final_state["jokes"])))

if __name__ == "__main__":
    prompt_config = load_yaml(filename=PROMPT_CONFIG_FILE_NAME)
    writer_model = WriterModel()
    main()
