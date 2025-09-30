from pydantic import BaseModel
from typing import List

class ColourAlert(BaseModel):
    channel: int
    linear_rgb: List[int]

class BloodAlert(BaseModel):
    channel: int
    isBlood: bool
