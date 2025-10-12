import json
from pathlib import Path
from typing import List

from StandardLibrary.PythonTypes import User

with open("web-backend/database/users.json", "r") as f:
    user_data = json.load(f)

users: List[User] = [User(**u) for u in user_data]
