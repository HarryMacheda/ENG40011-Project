from pydantic import BaseModel
from typing import List

class Colour(BaseModel):
    r: int
    g: int
    b: int

class ColourAlert(Colour):
    isBlood: bool

class PatientInfo(BaseModel):
    room: str
    firstName: str
    lastName: str
    bloodType: str

class User(BaseModel):
    username: str
    password: str
    scopes: List[str] = []