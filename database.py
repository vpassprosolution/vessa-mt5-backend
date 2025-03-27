import psycopg2
from datetime import datetime
import traceback  # ✅ Add for detailed error tracking

DATABASE_URL = "postgresql://postgres:vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb@interchange.proxy.rlwy.net:30451/railway"

def save_mt5_data(user_id: int, broker: str, login: str, password: str):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO mt5_accounts (user_id, broker, login, password, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET broker = EXCLUDED.broker,
                login = EXCLUDED.login,
                password = EXCLUDED.password,
                created_at = EXCLUDED.created_at;
        """, (user_id, broker, login, password, datetime.utcnow()))

        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ Failed to save MT5 data:", e)
        traceback.print_exc()  # ✅ Show full error trace
        return False


def save_risk_data(user_id: int, method: str, value: str):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO risk_preferences (user_id, method, value, created_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET method = EXCLUDED.method,
                value = EXCLUDED.value,
                created_at = EXCLUDED.created_at;
        """, (user_id, method, value, datetime.utcnow()))

        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ Failed to save risk data:", e)
        traceback.print_exc()  # ✅ Show full error trace
        return False
