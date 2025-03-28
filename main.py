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

# ✅ CORS setup for Mini App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Railway PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb@interchange.proxy.rlwy.net:30451/railway"
)

# ✅ MetaAPI credentials
METAAPI_TOKEN = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiJlZTFiMzY5MWExMTQzMTYzMjg1ZjYwNDBkYWVkMjFjZCIsImFjY2Vzc1J1bGVzIjpbeyJpZCI6InRyYWRpbmctYWNjb3VudC1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFhcGktcmVzdC1hcGkiLCJtZXRob2RzIjpbIm1ldGFhcGktYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFhcGktcnBjLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFhcGktcmVhbC10aW1lLXN0cmVhbWluZy1hcGkiLCJtZXRob2RzIjpbIm1ldGFhcGktYXBpOndzOnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtZXRhc3RhdHMtYXBpIiwibWV0aG9kcyI6WyJtZXRhc3RhdHMtYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6InJpc2stbWFuYWdlbWVudC1hcGkiLCJtZXRob2RzIjpbInJpc2stbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoiY29weWZhY3RvcnktYXBpIiwibWV0aG9kcyI6WyJjb3B5ZmFjdG9yeS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibXQtbWFuYWdlci1hcGkiLCJtZXRob2RzIjpbIm10LW1hbmFnZXItYXBpOnJlc3Q6ZGVhbGluZzoqOioiLCJtdC1tYW5hZ2VyLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJiaWxsaW5nLWFwaSIsIm1ldGhvZHMiOlsiYmlsbGluZy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfV0sImlnbm9yZVJhdGVMaW1pdHMiOmZhbHNlLCJ0b2tlbklkIjoiMjAyMTAyMTMiLCJpbXBlcnNvbmF0ZWQiOmZhbHNlLCJyZWFsVXNlcklkIjoiZWUxYjM2OTFhMTE0MzE2MzI4NWY2MDQwZGFlZDIxY2QiLCJpYXQiOjE3NDMxODM0Mzh9.AlE8ZC0wk2DTeAQWuo0bm1_DJcoE1hYyev7CYkGPCzGV_A-7zmg4VThdIb7dQ0gGew5o1dv8wEScTu7VO3ldETo4hXV3q3nloFNa_Dr5Vz4-gfmtNpxp_QwJ1yxbHaI6G3kE7yGGWjlF_pV9uepvCtDISMO0T10meZxK9pjLiFSKHgd-amaoVGdL5mUCEPdtj4CTle7UxETFYmLIR4dOMm0ozJ9IS8_Vfk0e90q-JBbsHIj-87QFh1-FfiXODKeBadOyiFf1O7PvCBnEjqVXrG2Em49Uh_GN1CHoBzusbTe6lfNbdQjuCDsgIWUEP2ZrPT9aZCfcRaS-N-7Beix8sUdkSzv3oRtgarNOLr2gtWjK5Q5tMUv9u9rLi8F6d7smNXALyZ1cmnNVJArSePXl6PCR8DxycgQapnwxIwHgwL-CD-DrFOpNaGHCzrgcxS5iuLLum2WOAzx6exRgx2stgcPt9O4uIRMuzWq00bbWueuVtLc5ksxcv3_0NlWfLc6tWXyznvvFFluSvj9CvXh1DKnSFODS0gp9sBcRMQ13lJ3K0RA8TBBjQEluoI9sbQi7bHHBHMPZKmDcQibFmwkqXRY8vGhbqZRDXfQXI6TiY_BNpQanPaomGKLZ7BjrLY4imdmQX4fDTMlosZNjEPwMw6rLc1CYdWMyWRnzJQ1LpNU"  # 🔒 Use your full token

# -------------------------------
@app.get("/")
def root():
    return {"message": "Hello from VESSA MT5 Backend ✅"}

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
        try:
            account = await metaapi.metatrader_account_api.get_account(metaapi_id)
            await account.reload()
            status = account.connection_status
        except Exception as e:
            # If MetaAPI account is deleted
            print(f"⚠️ Account ID {metaapi_id} not found. Cleaning DB...")
            cur.execute("""
                UPDATE users
                SET metaapi_account_id = NULL,
                    mt5_login = NULL,
                    mt5_password = NULL,
                    mt5_broker = NULL,
                    is_mt5_valid = FALSE
                WHERE user_id = %s
            """, (user_id,))
            conn.commit()
            return {"status": "deleted", "is_valid": False}

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
@app.post("/delete_mt5")
async def delete_mt5(user_id: int = Form(...)):
    try:
        success = await delete_mt5_account(user_id)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}

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
@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return RedirectResponse(url="/redoc")
