from pydantic import BaseModel
from typing import List

class Colour(BaseModel):
    r: int
    g: int
    b: int

class ColourAlert(Colour):
    isBlood: bool
