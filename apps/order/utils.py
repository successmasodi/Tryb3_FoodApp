import os
import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv('FLW_ENCRYPT_KEY')

def encrypt_token(payload):
    token = jwt.encode(payload, SECRET, algorithm='HS256')
    return token

def decrypt_token(token):
    try:
        payload = jwt.decode(token, SECRET, algorithms=['HS256'])
        return {'status': 'success', 'data': payload}
    except jwt.InvalidTokenError:
        return {'status': 'error', 'message': 'Invalid Token'}

def get_flutter_header():
    return {
            "Authorization": f"Bearer {os.getenv('FLW_SECRET_KEY')}", 
            "Content-Type": "application/json"
        }
