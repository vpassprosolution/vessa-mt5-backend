from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from database import save_mt5_data, save_risk_data
import psycopg2
import os

app = FastAPI()

# -------------------------------
# ✅ Root Endpoint
# -------------------------------
@app.get("/")
def root():
    return {"message": "Hello from VESSA MT5 Backend ✅"}


# -------------------------------
# ✅ Save MT5 Endpoint
# -------------------------------
class MT5Data(BaseModel):
    user_id: int
    broker: str
    login: str
    password: str

@app.post("/save_mt5")
async def save_mt5(data: MT5Data):
    success = await save_mt5_data(
        user_id=data.user_id,
        broker=data.broker,
        login=data.login,
        password=data.password
    )
    return {"success": success}


# -------------------------------
# ✅ Save Risk Endpoint
# -------------------------------
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


# -------------------------------
# ✅ Optional Redirect /docs fix
# -------------------------------
@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return RedirectResponse(url="/redoc")


# -------------------------------
# ✅ Get Premium Copy Users by Symbol
# -------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb@interchange.proxy.rlwy.net:30451/railway")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

@app.get("/get_users_by_symbol")
def get_users_by_symbol(symbol: str):
    try:
        cursor.execute("""
            SELECT chat_id, user_id FROM users 
            WHERE is_premium = true 
              AND mt5_login IS NOT NULL 
              AND mt5_broker IS NOT NULL 
              AND metaapi_account_id IS NOT NULL
        """)
        rows = cursor.fetchall()
        users = [{"chat_id": row[0], "user_id": row[1]} for row in rows]
        return {"users": users}
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# ✅ Set Copy Subscription (Subscribe/Unsubscribe)
# -------------------------------
class CopySubData(BaseModel):
    user_id: int
    status: bool

from database import set_copy_subscription_status  # make sure this exists

@app.post("/set_copy_subscription")
async def set_copy_subscription(data: CopySubData):
    try:
        success = set_copy_subscription_status(data.user_id, data.status)
        return {"success": success}
    except Exception as e:
        return {"error": str(e)}
