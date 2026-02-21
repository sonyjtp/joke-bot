# Joke Bot

A joke-telling chatbot built with LangGraph demonstrating stateful graph-based workflows. This project includes two implementations: a simple rule-based bot and an advanced bot using AI (writer + critic) for joke generation and evaluation.

## Project Structure

- **`joke_bot_simple.py`** – Simple rule-based joke bot using PyJokes library
- **`joke_bot_with_writer_critic.py`** – Advanced AI-driven bot with LLM writer and critic nodes

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd joke-bot
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Simple Joke Bot

Run the simple rule-based joke bot:
```bash
python src/joke_bot_simple.py
```

Features:
- Fetch random jokes from different categories (neutral, chuck, all)
- Interactive menu to get next joke, change category, or quit
- No LLM dependencies - uses PyJokes library for joke generation

Follow the on-screen prompts:
- `n`: Get the next joke
- `c`: Change joke category
- `q`: Quit the application

### JokeBot with Writer & Critic

Run the advanced AI-driven joke bot:
```bash
python src/joke_bot_with_writer_critic.py
```

This implementation features an agentic workflow with two specialized LLM nodes:

- **Writer Node** – Generates creative jokes based on selected category and language
- **Critic Node** – Evaluates jokes for quality and approves/rejects them
- **Interactive Menu** – Users can fetch jokes, update category/language, reset state, or exit

#### Workflow Diagram

```mermaid
flowchart TB
  subgraph UserFlow["User Interaction Flow"]
    SHOW_MENU["<b>show_menu</b><br/>(display choices)"]
    UPDATE_CATEGORY["<b>update_category</b><br/>(set joke category)"]
    UPDATE_LANGUAGE["<b>update_language</b><br/>(set language)"]
    RESET_STATE["<b>reset_state</b><br/>(clear history)"]
  end

  subgraph AIFlow["AI Generation & Evaluation"]
    WRITER["<b>writer</b> 🤖<br/>(generate joke)"]
    CRITIC["<b>critic</b> 🔍<br/>(evaluate quality)"]
  end

  subgraph Output["Output & Exit"]
    SHOW_JOKE["<b>show_final_joke</b><br/>(display approved joke)"]
    EXIT_BOT["<b>exit_bot</b><br/>(cleanup & exit)"]
    END(["END"])
  end

  %% styling
  classDef userNode fill:#e1f5ff,stroke:#01579b,stroke-width:2px
  classDef aiNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
  classDef outputNode fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
  classDef endNode fill:#ffe0b2,stroke:#e65100,stroke-width:2px

  class SHOW_MENU,UPDATE_CATEGORY,UPDATE_LANGUAGE,RESET_STATE userNode
  class WRITER,CRITIC aiNode
  class SHOW_JOKE,EXIT_BOT outputNode
  class END endNode

  %% conditional edges from show_menu (route_choice)
  SHOW_MENU -->|n: Fetch Joke| WRITER
  SHOW_MENU -->|c: Update Category| UPDATE_CATEGORY
  SHOW_MENU -->|l: Update Language| UPDATE_LANGUAGE
  SHOW_MENU -->|r: Reset State| RESET_STATE
  SHOW_MENU -->|q: Quit| EXIT_BOT

  %% edges back to menu
  UPDATE_CATEGORY --> SHOW_MENU
  UPDATE_LANGUAGE --> SHOW_MENU
  RESET_STATE --> SHOW_MENU

  %% main workflow
  WRITER --> CRITIC
  SHOW_JOKE --> SHOW_MENU
  EXIT_BOT --> END

  %% conditional edges from critic (route_critic_decision)
  CRITIC -->|APPROVED ✓| SHOW_JOKE
  CRITIC -->|REJECTED ✗| WRITER
```

**Key Features:**
- State-driven workflow using LangGraph
- Conditional routing based on user choice and critic decision
- Persistent state across multiple joke generations
- Critic re-routes rejected jokes back to writer for regeneration
- Configurable LLM models via `config.yaml`

## Requirements

- Python 3.12+
- Dependencies listed in `requirements.txt`

## License

[Add license information here]
