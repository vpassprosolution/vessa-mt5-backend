from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from database import save_mt5_data, save_risk_data  

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "✅ FastAPI is working!"}

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
    success = save_risk_data(
        user_id=data.user_id,
        method=data.method,
        value=data.value
    )
    return {"success": success}

# ✅ Optional: Redirect /docs to /redoc if needed
@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return RedirectResponse(url="/redoc")
