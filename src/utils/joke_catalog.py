import json
import os
from pathlib import Path

from src.joke_state import Joke

CATALOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CATALOG_FILE = os.path.join(CATALOG_DIR, "joke_catalog.json")


def ensure_catalog_dir_exists():
    """Ensure the catalog directory exists."""
    Path(CATALOG_DIR).mkdir(parents=True, exist_ok=True)


def load_catalog() -> list[dict]:
    """Load all jokes from the catalog file."""
    ensure_catalog_dir_exists()
    if os.path.exists(CATALOG_FILE):
        try:
            with open(CATALOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []


def save_joke_to_catalog(joke: Joke) -> bool:
    """Save a single joke to the catalog file."""
    ensure_catalog_dir_exists()
    catalog = load_catalog()

    joke_dict = joke.model_dump()

    # Check if joke already exists in catalog
    if any(j["text"] == joke_dict["text"] for j in catalog):
        print("📝 Joke already exists in catalog.")
        return False

    catalog.append(joke_dict)

    try:
        with open(CATALOG_FILE, "w", encoding="utf-8") as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        print(f"📚 Joke saved to catalog! (Total jokes: {len(catalog)})")
        return True
    except IOError as e:
        print(f"❌ Error saving joke to catalog: {e}")
        return False


def get_catalog_stats() -> dict:
    """Get statistics about the catalog."""
    catalog = load_catalog()

    stats = {
        "total_jokes": len(catalog),
        "by_category": {}
    }

    for joke in catalog:
        category = joke.get("category", "unknown")
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

    return stats


def display_catalog_stats():
    """Display catalog statistics to the user."""
    stats = get_catalog_stats()
    print("\n📚 JOKE CATALOG STATISTICS")
    print("=" * 60)
    print(f"Total jokes in catalog: {stats['total_jokes']}")
    if stats["by_category"]:
        print("\nJokes by category:")
        for category, count in sorted(stats["by_category"].items()):
            print(f"  • {category.upper()}: {count} jokes")
    else:
        print("No jokes in catalog yet.")
    print("=" * 60 + "\n")


def view_catalog_by_category(category: str = None) -> list[dict]:
    """View jokes from the catalog, optionally filtered by category."""
    catalog = load_catalog()

    if category:
        filtered = [j for j in catalog if j.get("category") == category]
        return filtered

    return catalog

