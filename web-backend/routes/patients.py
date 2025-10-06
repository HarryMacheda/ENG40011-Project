from fastapi import APIRouter, Depends, HTTPException, status

from StandardLibrary.PythonTypes import PatientInfo
from ..database.patients import patients
from ..authentication.tokens import TokenManager

router = APIRouter(
    prefix="/patients",
    tags=["patients"]
)


@router.get("/", response_model=list[PatientInfo])
async def get_all_patients(token:dict = Depends(TokenManager.requireScope("read"))):
    return patients

@router.get("/{room}", response_model=PatientInfo)
async def get_patient_by_room(room: str, token:dict = Depends(TokenManager.requireScope("read"))):
    for patient in patients:
        if patient.room == room:
            return patient
    raise HTTPException(status_code=404, detail=f"Patient in room {room} not found")
