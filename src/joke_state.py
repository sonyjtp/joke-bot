from operator import add
from typing import Annotated, Literal

from pydantic import BaseModel, Field
from pyjokes.pyjokes import CATEGORIES, LANGUAGES

CHOICES = Literal["n", "c", "l", "r", "q"]

class Joke(BaseModel):
    text: str
    category: str

class JokeState(BaseModel):
    jokes: Annotated[list[Joke], add] = Field(default_factory=list[Joke])
    choice:CHOICES  = "n"
    category: CATEGORIES = "neutral"
    language: LANGUAGES = "en"
    repetition: bool = False
    quit: bool = False

class AgenticJokeState(JokeState):
    latest_joke: str = ""
    approved: bool = False
    retry_count: int = 0