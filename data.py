# import requests
# import hashlib

# api_key = "836113cf8b984e6696e76b93d1bbbcac"
# api_secret = "2025.9c5af031bbb64e83b79f9887c641c6b5060ac56708d8c2b8"
# request_code = "184ef9ae60bc9a70.f2dc942b56c30370855a5568723601f7999c31662ec47beb94d2018c21a8aac2"


# # Correct checksum generation
# s = api_key + request_code + api_secret
# hash_secret = hashlib.sha256(s.encode('utf-8')).hexdigest()

# # Use checksum in payload
# payload = {
#     "api_key": api_key,
#     "request_code": request_code,
#     "checksum": hash_secret
# }

# url = "https://authapi.flattrade.in/trade/apitoken"
# response = requests.post(url, json=payload)

# print("STATUS CODE:", response.status_code)
# print("RESPONSE TEXT:", response.text)
# try:
#     print("JSON:", response.json())
# except Exception as e:
#     print("JSON Decode Error:", e)

from brokers.flattrade.api import FlatTradeApiPy
from login import flattrade_login
import json



from login import flattrade_login

print("🟢 File loaded")

if __name__ == "__main__":
    print("🚀 Inside main block")
    api = flattrade_login()
    print("🔵 flattrade_login() returned:", api)
