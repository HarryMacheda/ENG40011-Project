from ..authentication.tokens import Token, TokenManager
from ..authentication.clients import ApiClientStore
from fastapi import APIRouter, Depends, HTTPException, status, Form

router = APIRouter(
    prefix="/auth",
    tags=["authentication, token, permissions"]
)

@router.post("/token", response_model=Token)
async def issue_token(
    grant_type: str = Form(..., regex="client_credentials"),
    client_id: str = Form(...),
    client_secret: str = Form(...),
):
    client = ApiClientStore().getClient(client_id, client_secret)
    access_token = TokenManager().generateAccessToken({"sub": client_id, "scopes": client["scopes"]})

    return {"access_token": access_token, "token_type": "bearer"}



@router.get("/token-validate")
async def secure_data(token:dict = Depends(TokenManager().getCurrentToken)):
    client_id = token.get("sub")
    return {"detail": f"This is avalid token for {client_id}"}