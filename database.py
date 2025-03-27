import psycopg2
from datetime import datetime
import traceback
from metaapi_cloud_sdk import MetaApi

DATABASE_URL = "postgresql://postgres:vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb@interchange.proxy.rlwy.net:30451/railway"

# ✅ MetaAPI credentials
METAAPI_TOKEN = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiJlZTFiMzY5MWExMTQzMTYzMjg1ZjYwNDBkYWVkMjFjZCIsImFjY2Vzc1J1bGVzIjpbeyJpZCI6Im1ldGFhcGktcmVzdC1hcGkiLCJtZXRob2RzIjpbIm1ldGFhcGktYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6ImNvcHlmYWN0b3J5LWFwaSIsIm1ldGhvZHMiOlsiY29weWZhY3RvcnktYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX1dLCJpZ25vcmVSYXRlTGltaXRzIjpmYWxzZSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaW1wZXJzb25hdGVkIjpmYWxzZSwicmVhbFVzZXJJZCI6ImVlMWIzNjkxYTExNDMxNjMyODVmNjA0MGRhZWQyMWNkIiwiaWF0IjoxNzQzMDg0ODcyfQ.jOsIFdN0w0IuCbgaLK4S3dG0vtyIn_dou9rul88pj05me4pnDSiPC4EjkIQyuwEHU9Sqy2BVnwDYaqRszi5UYMWpCro3IQxeIBe-tcDGP0QGKvsk7153OYKQbwQpyXxsQ_T6UMTBiwepaFbAjFViovxSjO0879zriIkZ21FOtxFGRtsejO1gWJ9GJ50o6EPc64Fu6h_IDuBeChUhQi-oOwg8n8ZPYBa2c1Q43X7oi_viKbFslvLwUPeKrSxu-NIdl5eGHg8lHnznuFxck28_NsXTgN4EY_vN-NXtrbtqhwzBGGpYCsqDlc-gPlpytLXsrx1C-WR_Di55CxDt8S5IPph53kPberd8NB3LVGjqj6UR5mFS1pDYl9eOl9hzm-WpIZxW5c0PDtWxvRdEjOlWblmw79yOu37djik_bUYssOVVpvPXqds65zctCe-6Bs4sUt02KKkJCLdrr0edAvu6OToaYJ4jdp3HLethhjTsd9QRuNeq0PFIeJuqt2F7JN9GqhZCG3lZxOv3vmwV1GbdKtpm3v6RCY9TbQG-H6UAMLCAV4kbKpG5qr5XJXiC_EI8wFrJLRGVRBgy6ic_9gKUua3o6E2DYKfC8nqLvzZa-4hwqGqpbpuRMtuYl7W1812Uiv38sP1Xc_i0KgiWJYm7vTr-dD3ESWxwRbaXMAuorYs"  # ⚠️ Replace with your real token

# ✅ Save MT5 account to 'users' table and create MetaAPI ID
async def save_mt5_data(user_id: int, broker: str, login: str, password: str):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 🔧 Step 1: Create MetaAPI account
        metaapi = MetaApi(METAAPI_TOKEN)
        account = await metaapi.metatrader_account_api.create_account({
            'name': f'VESSA-{login}',
            'type': 'cloud',
            'login': login,
            'password': password,
            'server': broker,
            'platform': 'mt5',
            'application': 'copyfactory',
            'magic': 123456
        })
        metaapi_id = account['id']

        # 🔧 Step 2: Save all to `users` table
        cur.execute("""
            UPDATE users
            SET mt5_broker = %s,
                mt5_login = %s,
                mt5_password = %s,
                metaapi_account_id = %s
            WHERE user_id = %s;
        """, (broker, login, password, metaapi_id, user_id))

        conn.commit()
        cur.close()
        conn.close()
        return True

    except Exception as e:
        print("❌ Failed to save MT5 data:", e)
        traceback.print_exc()
        return False


# ✅ Save risk preference to `users` table
def save_risk_data(user_id: int, method: str, value: str):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("""
            UPDATE users
            SET risk_type = %s,
                risk_value = %s
            WHERE user_id = %s;
        """, (method, value, user_id))

        conn.commit()
        cur.close()
        conn.close()
        return True

    except Exception as e:
        print("❌ Failed to save risk data:", e)
        traceback.print_exc()
        return False

def set_copy_subscription_status(user_id: int, status: bool):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            UPDATE users
            SET is_copy_subscribed = %s
            WHERE user_id = %s
        """, (status, user_id))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ Error updating subscription status:", e)
        return False
