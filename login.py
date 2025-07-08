from brokers.flattrade.api import FlatTradeApiPy
from brokers.flattrade.api import get_cred, USER, PWD, TOTP_KEY, API_SECRET
import pyotp
import json
import os
 # True = Paper Trading,
#api_obj = FlatTradeApiPy(emulation=True)



def flattrade_login():
    print("🚀 Starting Flattrade login")

    # Path to your credentials
    cred_path = "config/flattrade_config.json"

    if not os.path.exists(cred_path):
        print(f"❌ Credentials file not found at {cred_path}")
        return None

    try:
        with open(cred_path) as f:
            creds = json.load(f)

        userid = creds.get("userid")
        password = creds.get("password")
        totp_key = creds.get("twoFAKey")
        api_secret = creds.get("api_secret")
        vendor_code = creds.get("vendor_code", "FZ19143_U")
        imei = creds.get("imei", "abc1234")

        if not all([userid, password, totp_key]):
            print("❌ Missing credentials. Please check your JSON file.")
            return None

        # Generate TOTP
        totp = pyotp.TOTP(totp_key).now()
        print(f"🔐 TOTP: {totp}")

        # Create API object
        api_obj = FlatTradeApiPy(emulation=False)

        # 🔁 Attempt login
        res = api_obj.login(
            userid=userid,
            password=password,
            twoFA=totp,
            vendor_code=vendor_code,
            api_secret=api_secret,
            imei=imei
        )

        # 📡 Show full response
        print("📡 Login Response:")
        print(json.dumps(res, indent=2) if res else "⚠️ No response received")

        if res and res.get("stat") == "Ok":
            print("✅ Token generated successfully")
            return api_obj
        else:
            print(f"❌ Login failed: {res.get('emsg') if res else 'No response'}")
            return None

    except Exception as e:
        print("💥 Exception during login:", str(e))
        return None

if __name__ == "__main__":
    api = flattrade_login()
    if api:
        print(" API object is ready to use")
    else:
        print(" API object is None – login failed")