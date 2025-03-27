from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from database import save_mt5_data, save_risk_data  

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

# 📦 Define expected request format
class MT5Data(BaseModel):
    user_id: int
    broker: str
    login: str
    password: str

@app.post("/save_mt5")
async def save_mt5(data: MT5Data):
    success = save_mt5_data(
        user_id=data.user_id,
        broker=data.broker,
        login=data.login,
        password=data.password
    )
    return {"success": success}

class RiskData(BaseModel):
    user_id: int
    method: str
    value: str

@app.post("/save_risk")
async def save_risk(data: RiskData):
    success = save_risk_data(
        user_id=data.user_id,
        method=data.method,
        value=data.value
    )
    return {"success": success}

@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return RedirectResponse(url="/redoc")
