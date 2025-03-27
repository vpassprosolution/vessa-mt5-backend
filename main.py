from fastapi import FastAPI, Request
from pydantic import BaseModel
from database import save_mt5_data, save_risk_data  # Make sure save_risk_data is defined in your database.py

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

# ✅ API to receive and save MT5 account info
@app.post("/save_mt5")
async def save_mt5(data: MT5Data):
    success = save_mt5_data(
        user_id=data.user_id,
        broker=data.broker,
        login=data.login,
        password=data.password
    )
    return {"success": success}

# 📦 Define expected request format for Risk data
class RiskData(BaseModel):
    user_id: int
    method: str
    value: str

# ✅ API to receive and save Risk preference info
@app.post("/save_risk")
async def save_risk(data: RiskData):
    success = save_risk_data(  # Ensure this function is defined in your database.py
        user_id=data.user_id,
        method=data.method,
        value=data.value
    )
    return {"success": success}

