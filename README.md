# Joke Bot

A simple joke-telling chatbot built with LangGraph and PyJokes. This project demonstrates a stateful graph-based workflow for interactive applications without using large language models.

## Features

- Fetch random jokes from different categories (neutral, chuck, all)
- Interactive menu to get next joke, change category, or quit
- Built using LangGraph for state management and workflow control
- No LLM dependencies - uses PyJokes library for joke generation

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

Run the joke bot:
```bash
python src/joke_bot.py
```

Follow the on-screen prompts:
- `n`: Get the next joke
- `c`: Change joke category
- `q`: Quit the application

## Requirements

- Python 3.12+
- Dependencies listed in `requirements.txt`

## License

[Add license information here]
