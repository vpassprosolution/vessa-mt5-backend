from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from database import save_mt5_data, save_risk_data
import psycopg2

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
    success = save_mt5_data(
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
# ✅ Get Users by Symbol Endpoint
# -------------------------------
# ✅ Filled in your Railway PostgreSQL URL here
DATABASE_URL = "postgresql://postgres:vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb@interchange.proxy.rlwy.net:30451/railway"
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

@app.get("/get_users_by_symbol")
def get_users_by_symbol(symbol: str):
    try:
        cursor.execute("SELECT chat_id, instrument FROM subscribers WHERE instrument = %s", (symbol.upper(),))
        rows = cursor.fetchall()
        users = [{"chat_id": row[0], "instrument": row[1]} for row in rows]
        return {"users": users}
    except Exception as e:
        return {"error": str(e)}
