import psycopg2
from datetime import datetime
import traceback
from metaapi_cloud_sdk import MetaApi
import asyncio

# ✅ PostgreSQL connection
DATABASE_URL = "postgresql://postgres:vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb@interchange.proxy.rlwy.net:30451/railway"

# ✅ MetaAPI credentials
METAAPI_TOKEN = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiJlZTFiMzY5MWExMTQzMTYzMjg1ZjYwNDBkYWVkMjFjZCIsImFjY2Vzc1J1bGVzIjpbeyJpZCI6InRyYWRpbmctYWNjb3VudC1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFhcGktcmVzdC1hcGkiLCJtZXRob2RzIjpbIm1ldGFhcGktYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFhcGktcnBjLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFhcGktcmVhbC10aW1lLXN0cmVhbWluZy1hcGkiLCJtZXRob2RzIjpbIm1ldGFhcGktYXBpOndzOnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtZXRhc3RhdHMtYXBpIiwibWV0aG9kcyI6WyJtZXRhc3RhdHMtYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6InJpc2stbWFuYWdlbWVudC1hcGkiLCJtZXRob2RzIjpbInJpc2stbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoiY29weWZhY3RvcnktYXBpIiwibWV0aG9kcyI6WyJjb3B5ZmFjdG9yeS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibXQtbWFuYWdlci1hcGkiLCJtZXRob2RzIjpbIm10LW1hbmFnZXItYXBpOnJlc3Q6ZGVhbGluZzoqOioiLCJtdC1tYW5hZ2VyLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJiaWxsaW5nLWFwaSIsIm1ldGhvZHMiOlsiYmlsbGluZy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfV0sImlnbm9yZVJhdGVMaW1pdHMiOmZhbHNlLCJ0b2tlbklkIjoiMjAyMTAyMTMiLCJpbXBlcnNvbmF0ZWQiOmZhbHNlLCJyZWFsVXNlcklkIjoiZWUxYjM2OTFhMTE0MzE2MzI4NWY2MDQwZGFlZDIxY2QiLCJpYXQiOjE3NDMxODM0Mzh9.AlE8ZC0wk2DTeAQWuo0bm1_DJcoE1hYyev7CYkGPCzGV_A-7zmg4VThdIb7dQ0gGew5o1dv8wEScTu7VO3ldETo4hXV3q3nloFNa_Dr5Vz4-gfmtNpxp_QwJ1yxbHaI6G3kE7yGGWjlF_pV9uepvCtDISMO0T10meZxK9pjLiFSKHgd-amaoVGdL5mUCEPdtj4CTle7UxETFYmLIR4dOMm0ozJ9IS8_Vfk0e90q-JBbsHIj-87QFh1-FfiXODKeBadOyiFf1O7PvCBnEjqVXrG2Em49Uh_GN1CHoBzusbTe6lfNbdQjuCDsgIWUEP2ZrPT9aZCfcRaS-N-7Beix8sUdkSzv3oRtgarNOLr2gtWjK5Q5tMUv9u9rLi8F6d7smNXALyZ1cmnNVJArSePXl6PCR8DxycgQapnwxIwHgwL-CD-DrFOpNaGHCzrgcxS5iuLLum2WOAzx6exRgx2stgcPt9O4uIRMuzWq00bbWueuVtLc5ksxcv3_0NlWfLc6tWXyznvvFFluSvj9CvXh1DKnSFODS0gp9sBcRMQ13lJ3K0RA8TBBjQEluoI9sbQi7bHHBHMPZKmDcQibFmwkqXRY8vGhbqZRDXfQXI6TiY_BNpQanPaomGKLZ7BjrLY4imdmQX4fDTMlosZNjEPwMw6rLc1CYdWMyWRnzJQ1LpNU"  # 🔒 Use your full token

# ✅ Save MT5 account to 'users' table and create MetaAPI ID
async def save_mt5_data(user_id: int, broker: str, login: str, password: str):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 🔍 Step 1: Check existing MetaAPI account
        cur.execute("SELECT metaapi_account_id FROM users WHERE user_id = %s", (user_id,))
        result = cur.fetchone()
        old_account_id = result[0] if result else None

        metaapi = MetaApi(METAAPI_TOKEN)

        # 🗑️ Step 2: Delete old account if exists
        if old_account_id:
            try:
                await metaapi.metatrader_account_api.remove_account(old_account_id)
                print(f"🗑️ Old MetaAPI account deleted: {old_account_id}")
            except Exception as del_error:
                print("⚠️ Warning: Failed to delete old MetaAPI account:", del_error)

        # ⚙️ Step 3: Create new account
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
        metaapi_id = account.id
        print(f"✅ MetaAPI Account Created: {metaapi_id}")

        # 💾 Step 4: Save details to DB immediately (set is_mt5_valid = FALSE first)
        cur.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if not cur.fetchone():
            cur.execute("INSERT INTO users (user_id) VALUES (%s)", (user_id,))
            conn.commit()

        cur.execute("""
            UPDATE users SET
                mt5_broker = %s,
                mt5_login = %s,
                mt5_password = %s,
                metaapi_account_id = %s,
                is_mt5_valid = FALSE,
                risk_type = COALESCE(risk_type, 'fixed'),
                risk_value = COALESCE(risk_value, '0.01')
            WHERE user_id = %s;
        """, (broker, login, password, metaapi_id, user_id))
        conn.commit()

        # ⏳ Step 5: Try to wait for connection up to 30s
        print("⏳ Waiting for MetaAPI to connect...")
        connected = False
        for attempt in range(30):
            await account.reload()
            status = account.connection_status
            print(f"🔁 Attempt {attempt + 1}: {status}")
            if status.lower() == "connected":
                cur.execute("UPDATE users SET is_mt5_valid = TRUE WHERE user_id = %s", (user_id,))
                conn.commit()
                print("✅ MetaAPI Connected. Marked as valid.")
                connected = True
                break
            await asyncio.sleep(1)

        if not connected:
            print("⚠️ Still disconnected after 30s. Leaving is_mt5_valid = FALSE")

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

        # ✅ Ensure user row exists
        cur.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if not cur.fetchone():
            cur.execute("INSERT INTO users (user_id) VALUES (%s)", (user_id,))
            conn.commit()

        # ✅ Save risk method + value
        cur.execute("""
            UPDATE users SET
                risk_type = %s,
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



# ✅ Set Copy Subscription status
def set_copy_subscription_status(user_id: int, status: bool):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            UPDATE users
            SET is_copy_subscribed = %s
            WHERE user_id = %s;
        """, (status, user_id))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ Error updating subscription status:", e)
        traceback.print_exc()
        return False

# ✅ Delete MT5 account from MetaAPI + DB cleanup
async def delete_mt5_account(user_id: int):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 🔍 Fetch metaapi_account_id
        cur.execute("SELECT metaapi_account_id FROM users WHERE user_id = %s", (user_id,))
        result = cur.fetchone()
        metaapi_id = result[0] if result else None

        if metaapi_id:
            try:
                metaapi = MetaApi(METAAPI_TOKEN)
                await metaapi.metatrader_account_api.remove_account(metaapi_id)
                print(f"🗑️ MetaAPI account deleted: {metaapi_id}")
            except Exception as del_error:
                print("⚠️ Failed to delete from MetaAPI:", del_error)

        # 🧹 Clean up fields in DB
        cur.execute("""
            UPDATE users
            SET mt5_login = NULL,
                mt5_password = NULL,
                mt5_broker = NULL,
                metaapi_account_id = NULL,
                is_copy_subscribed = FALSE
            WHERE user_id = %s;
        """, (user_id,))

        conn.commit()
        cur.close()
        conn.close()
        return True

    except Exception as e:
        print("❌ Error deleting MT5 account:", e)
        traceback.print_exc()
        return False
