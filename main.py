from fastapi import FastAPI, Request
from pydantic import BaseModel
from database import save_mt5_data

app = FastAPI()

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
