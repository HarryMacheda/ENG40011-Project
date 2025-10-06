import json
from pydantic import BaseModel
from typing import List

from StandardLibrary.PythonTypes import PatientInfo


with open("web-backend/database/patients.json", "r") as f:
    patients_data = json.load(f)

patients: List[PatientInfo] = [PatientInfo(**p) for p in patients_data]
