from fastapi import FastAPI, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import (
    save_mt5_data,
    save_risk_data,
    set_copy_subscription_status,
    delete_mt5_account
)
from metaapi_cloud_sdk import MetaApi
import psycopg2
import traceback
import os

app = FastAPI()

# 🛡️ CORS settings for Mini App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 Environment DB
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb@interchange.proxy.rlwy.net:30451/railway"
)

# 🔑 MetaAPI Token
METAAPI_TOKEN = os.getenv("METAAPI_TOKEN", "your_real_metaapi_token_here")  # ✅ Replace

# -------------------------------
# ✅ Root
# -------------------------------
@app.get("/")
def root():
    return {"message": "Hello from VESSA MT5 Backend ✅"}

# -------------------------------
# ✅ Check MT5 Status
# -------------------------------
@app.get("/check_mt5_status")
async def check_mt5_status(user_id: int):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("SELECT metaapi_account_id, is_mt5_valid FROM users WHERE user_id = %s", (user_id,))
        result = cur.fetchone()
        if not result:
            return {"status": "not_found", "is_valid": False}

        metaapi_id, is_valid = result
        if not metaapi_id:
            return {"status": "no_account", "is_valid": False}

        metaapi = MetaApi(METAAPI_TOKEN)
        account = await metaapi.metatrader_account_api.get_account(metaapi_id)
        await account.reload()
        status = account.connection_status

        print(f"📡 User {user_id} | MetaAPI Status: {status} | is_valid: {is_valid}")
        return {"status": status, "is_valid": is_valid}

    except Exception as e:
        print("❌ Error checking status:", e)
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": "Server error"})

    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

# -------------------------------
# ✅ Save MT5 Form
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

# -------------------------------
# ✅ Save Risk Form
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
# ✅ Delete MT5
# -------------------------------
@app.post("/delete_mt5")
async def delete_mt5(user_id: int = Form(...)):
    try:
        success = await delete_mt5_account(user_id)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}

# -------------------------------
# ✅ Get Premium Copy Users
# -------------------------------
@app.get("/get_users_by_symbol")
def get_users_by_symbol(symbol: str):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            SELECT chat_id, user_id FROM users 
            WHERE is_premium = true 
              AND mt5_login IS NOT NULL 
              AND mt5_broker IS NOT NULL 
              AND metaapi_account_id IS NOT NULL
        """)
        rows = cur.fetchall()
        users = [{"chat_id": row[0], "user_id": row[1]} for row in rows]
        cur.close()
        conn.close()
        return {"users": users}
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# ✅ Set Copy Subscription
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

# -------------------------------
# ✅ Redirect /docs → /redoc
# -------------------------------
@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return RedirectResponse(url="/redoc")
