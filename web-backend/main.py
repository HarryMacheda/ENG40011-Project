from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import authentication, liquid

app = FastAPI()

#TODO UPDATE TO LIMIT ORIGINS IN PROD
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.get("/ping")
async def ping(): 
    return {"message": "pong"}

app.include_router(authentication.router)
app.include_router(liquid.router)
