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

This implementation features an agentic workflow with specialized LLM nodes, duplicate detection, and joke persistence:

- **Writer Node** – Generates creative jokes based on selected category and language
- **Repetition Check Node** – Detects duplicate jokes against history
- **Critic Node** – Replaced with human approval (user approves/rejects jokes)
- **Joke Catalog** – Persists all approved jokes to a JSON file
- **Interactive Menu** – Users can fetch jokes, update category/language, browse catalog, reset state, or exit

#### Workflow Diagram

```mermaid
flowchart TB
  subgraph UserFlow["User Interaction Flow"]
    SHOW_MENU["<b>show_menu</b><br/>(display choices)"]
    UPDATE_CATEGORY["<b>update_category</b><br/>(set joke category)"]
    UPDATE_LANGUAGE["<b>update_language</b><br/>(set language)"]
    RESET_STATE["<b>reset_state</b><br/>(clear history)"]
    VIEW_CATALOG["<b>view_catalog</b><br/>(browse jokes)"]
  end

  subgraph AIFlow["AI Generation & Evaluation"]
    WRITER["<b>writer</b> 🤖<br/>(generate joke)"]
    CHECK_REP["<b>check_repetition</b> 🔄<br/>(detect duplicates)"]
    CRITIC["<b>critic</b> 👤<br/>(human approval)"]
  end

  subgraph Output["Output & Exit"]
    SHOW_JOKE["<b>show_joke</b> 💾<br/>(display & persist)"]
    EXIT_BOT["<b>exit_bot</b><br/>(cleanup & exit)"]
    END(["END"])
  end

  %% styling
  classDef userNode fill:#e1f5ff,stroke:#01579b,stroke-width:2px
  classDef aiNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
  classDef outputNode fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
  classDef endNode fill:#ffe0b2,stroke:#e65100,stroke-width:2px

  class SHOW_MENU,UPDATE_CATEGORY,UPDATE_LANGUAGE,RESET_STATE,VIEW_CATALOG userNode
  class WRITER,CHECK_REP,CRITIC aiNode
  class SHOW_JOKE,EXIT_BOT outputNode
  class END endNode

  %% conditional edges from show_menu (route_choice)
  SHOW_MENU -->|n: Fetch Joke| WRITER
  SHOW_MENU -->|c: Update Category| UPDATE_CATEGORY
  SHOW_MENU -->|l: Update Language| UPDATE_LANGUAGE
  SHOW_MENU -->|b: Browse Catalog| VIEW_CATALOG
  SHOW_MENU -->|r: Reset State| RESET_STATE
  SHOW_MENU -->|q: Quit| EXIT_BOT

  %% edges back to menu
  UPDATE_CATEGORY --> SHOW_MENU
  UPDATE_LANGUAGE --> SHOW_MENU
  RESET_STATE --> SHOW_MENU
  VIEW_CATALOG --> SHOW_MENU

  %% main workflow with repetition check
  WRITER --> CHECK_REP
  CHECK_REP -->|No Duplicate ✓| CRITIC
  CHECK_REP -->|Duplicate Found ✗| WRITER
  SHOW_JOKE --> SHOW_MENU
  EXIT_BOT --> END

  %% conditional edges from critic (route_critic_decision)
  CRITIC -->|APPROVED ✓| SHOW_JOKE
  CRITIC -->|REJECTED ✗| WRITER
```

**Key Features:**
- State-driven workflow using LangGraph
- Conditional routing based on user choice, repetition check, and human approval
- **Duplicate detection** – Prevents telling the same joke twice
- **Joke Catalog** – Automatically persists all approved jokes to `src/data/joke_catalog.json`
- **Browse Catalog** – Users can view catalog statistics and filter jokes by category
- Persistent state across multiple joke generations
- Configurable LLM models via `config.yaml`

**Joke Catalog Details:**
- All approved jokes are automatically saved to `src/data/joke_catalog.json` in JSON format
- Duplicates within the catalog are automatically detected and prevented
- Users can browse the catalog and filter jokes by category (neutral, chuck, all)
- Catalog statistics show total joke count and breakdown by category
- The catalog persists across sessions, allowing users to build a collection of their favorite jokes

**Menu Options:**
- `n` – Fetch next joke (generates, checks for duplicates, and gets human approval)
- `c` – Change joke category
- `l` – Change language
- `b` – Browse and view saved jokes from the catalog
- `r` – Reset state (clears session jokes but preserves catalog)
- `q` – Exit the application

**Human Approval Workflow:**
- After a joke is generated and passes the repetition check, the user approves or rejects it
- Approved jokes are immediately saved to the catalog
- Rejected jokes trigger the writer to generate a new one
- Up to 5 retry attempts before forcing approval

## Requirements

- Python 3.12+
- Dependencies listed in `requirements.txt`

## License

[Add license information here]
