from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt 

from authentication.tokens import Token, TokenManager
from authentication.clients import ApiClientStore
app = FastAPI()

@app.post("/token", response_model=Token)
async def issue_token(
    grant_type: str = Form(..., regex="client_credentials"),
    client_id: str = Form(...),
    client_secret: str = Form(...),
):
    client = ApiClientStore().getClient(client_id, client_secret)
    access_token = TokenManager().generateAccessToken({"sub": client_id, "scopes": client["scopes"]})

    return {"access_token": access_token, "token_type": "bearer"}



@app.get("/token-validate")
async def secure_data(client_id:str = Depends(TokenManager().getCurrentToken)):
    return {"detail": f"This is avalid token for {client_id}"}
