from pydantic import BaseModel

class Colour(BaseModel):
    r: int
    g: int
    b: int

class ColourAlert(Colour):
    isBlood: bool