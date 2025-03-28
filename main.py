from fastapi import FastAPI, Form
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from database import save_mt5_data, save_risk_data, set_copy_subscription_status
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
# ✅ Save MT5 Form Submission
# -------------------------------
@app.post("/save_mt5")
async def save_mt5(
    user_id: int = Form(...),
    broker: str = Form(...),
    login: str = Form(...),
    password: str = Form(...)
):
    success = await save_mt5_data(
        user_id=user_id,
        broker=broker,
        login=login,
        password=password
    )
    return {"success": success}

# -------------------------------
# ✅ Save Risk Form Submission
# -------------------------------
@app.post("/save_risk")
async def save_risk(
    user_id: int = Form(...),
    method: str = Form(...),
    value: str = Form(...)
):
    success = save_risk_data(
        user_id=user_id,
        method=method,
        value=value
    )
    return {"success": success}

# -------------------------------
# ✅ Optional Redirect for /docs
# -------------------------------
@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return RedirectResponse(url="/redoc")

# -------------------------------
# ✅ Get Premium Copy Users by Symbol
# -------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb@interchange.proxy.rlwy.net:30451/railway"
)
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
# ✅ Set Copy Subscription (API called by bot)
# -------------------------------
class CopySubData(BaseModel):
    user_id: int
    status: bool

@app.post("/set_copy_subscription")
async def set_copy_subscription(data: CopySubData):
    try:
        success = set_copy_subscription_status(data.user_id, data.status)
        return {"success": success}
    except Exception as e:
        return {"error": str(e)}
