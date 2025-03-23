import os
import json
import firebase_admin
from firebase_admin import credentials


firebase_creds = os.environ.get("FIREBASE_CREDENTIALS_JSON")
if not firebase_creds:
    raise ValueError("FIREBASE_CREDENTIALS_JSON environment variable is not set.")

# Parse the JSON string into a dictionary
service_account_info = json.loads(firebase_creds)
# print(service_account_info)

cred = credentials.Certificate(service_account_info)
# print(cred)
firebase_admin.initialize_app(cred)

print("Firebase Admin SDK initialized successfully.")