from fastapi import HTTPException, status

#CONST CLIENTS
#TODO MOVE TO IN-MEM DB FOR PROD
CLIENT_STORE = {
    "web_connector": {
        "client_secret": "f9dd5c32e1cf443a9d99bce763e31d64",
        "scopes": ["read"],
    },
    "device_connector": {
        "client_secret": "82b9e9e2558940df96a813ff69e7dfd4",
        "scopes": ["write"],
    },
    "testing_connector": {
        "client_secret": "1ee9435f3e8440299a96ce7853f01ec9",
        "scopes": ["read", "write"],
    },
}

class ApiClientStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def getClient(self, client_id:str, client_secret:str):
        client = CLIENT_STORE.get(client_id)
        if not client or client_secret != client["client_secret"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid client credentials",
            )
        return client
    
    def isValidClient(self, client_id:str):
        if client_id is None or client_id not in CLIENT_STORE:
            return False
        
        return True