import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import config

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from services import payload

app = FastAPI(
    title="ODS - Ver2-A2 API",
    version="0.1.0",
    description="API FastAPI para o projeto Ver2-A2",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def validate_user_password(userid: int, password: str):
    if password != "teste" or userid != 1:
        raise HTTPException(status_code=401, detail="Invalid password or user")

@app.get("/")
def index():
    return "Working"


@app.get("/get-payloads", dependencies=[Depends(validate_user_password)])
def get_payloads(userid: int, password: str):
    return payload.get_payloads(userid=userid, length=config.PAYLOAD_BATCH_SIZE)

@app.get("/get-payload", dependencies=[Depends(validate_user_password)])
def get_payload(userid: int, password: str):
    return payload.get_payloads(userid=userid, length=1)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.IP_ADRESS, port=config.PORT, reload=True)