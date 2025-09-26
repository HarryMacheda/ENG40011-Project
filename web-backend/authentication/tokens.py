from datetime import datetime, timedelta
from typing import List
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import BaseModel
from authentication.clients import ApiClientStore

# Config
#TODO MOVE TO ENV VARIABLES FOR PROD
SECRET_KEY = "611ad6aae2c242bc9a29d6edf7168669"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def getTokenExpiry(self):
        return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    def generateAccessToken(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + (self.getTokenExpiry())
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    def decodeAccessToken(self, token:str):
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    def getCurrentToken(self, token: str = Depends(oauth2_scheme)):
        try:
            payload =  TokenManager().decodeAccessToken(token)
            client_id: str = payload.get("sub")
            if not ApiClientStore().isValidClient(client_id):
                raise HTTPException(status_code=401, detail="Invalid token")
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
    def requireScope(scope: str):
        def wrapper(token: dict = Depends(TokenManager().getCurrentToken)):    
            return TokenManager.checkScope(token, scope)
        return wrapper
    
    def checkScope(token:dict, scope:str):
        scopes: List[str] = token.get("scopes", [])
        if scope not in scopes:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return token 