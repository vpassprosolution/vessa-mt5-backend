from fastapi import FastAPI, Form
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from database import save_mt5_data, save_risk_data, set_copy_subscription_status, delete_mt5_account
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
    user_id: str = Form(...),
    broker: str = Form(...),
    login: str = Form(...),
    password: str = Form(...)
):
    try:
        user_id = int(user_id)
        success = await save_mt5_data(user_id=user_id, broker=broker, login=login, password=password)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ✅ Check if user has MT5 connected
@app.get("/check_mt5_status")
def check_mt5_status(user_id: int):
    try:
        cursor.execute("""
            SELECT metaapi_account_id FROM users
            WHERE user_id = %s AND metaapi_account_id IS NOT NULL
        """, (user_id,))
        result = cursor.fetchone()
        return {"connected": bool(result)}
    except Exception as e:
        return {"connected": False, "error": str(e)}



# -------------------------------
# ✅ Save Risk Form Submission
# -------------------------------
@app.post("/save_risk")
async def save_risk(
    user_id: str = Form(...),
    method: str = Form(...),
    value: str = Form(...)
):
    try:
        user_id = int(user_id)
        success = save_risk_data(user_id=user_id, method=method, value=value)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}

# -------------------------------
# ✅ Delete MT5 Account (Step 3)
# -------------------------------
@app.post("/delete_mt5")
async def delete_mt5(user_id: int = Form(...)):
    try:
        success = await delete_mt5_account(user_id)
        if success:
            return JSONResponse(content={"success": True})
        else:
            return JSONResponse(content={"success": False, "error": "Delete failed"})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)})

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
# ✅ Set Copy Subscription (called by bot)
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
        return {"success": False, "error": str(e)}
