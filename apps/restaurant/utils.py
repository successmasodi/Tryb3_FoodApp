import os
import urllib.parse
import uuid
import jwt
from dotenv import load_dotenv

from .models import Cart
load_dotenv()

SECRET = os.getenv('FLW_ENCRYPT_KEY')

def encrypt_token(payload):
    token = jwt.encode(payload, SECRET, algorithm='HS256')
    return token


def decrypt_token(token):
    try:
        payload = jwt.decode(token, SECRET, algorithms=['HS256'])
        return {'status': 'success', 'data': payload}
    except jwt.ExpiredSignatureError:
        return {'status': 'error', 'message': 'Token Expired'}
    except jwt.InvalidTokenError:
        return {'status': 'error', 'message': 'Invalid Token'}


def get_payment_auth_headers():
    '''return auth header for payment'''
    return {
        "Authorization": f"Bearer {os.getenv('FLW_SECRET_KEY')}", 
        "Content-Type": "application/json"
        }


def generate_payment_data(cart: Cart):
    '''
    generate body for flutterwave payment gateway
    '''
    cart_id = str(cart.id)
    cart_total = str(cart.total)

    # success_url = request.build_absolute_uri('/api/v1/carts/{cart.id}/checkout/') use in production
    payload = {'cart_id': cart_id, 'total': cart_total}
    redirect_url = f'http:/localhost:8000/api/v1/carts/{cart_id}/confirm_payment?c_id={cart_id}&token={urllib.parse.quote(encrypt_token(payload=payload))}'

    return {
        "tx_ref": str(uuid.uuid4()),
        "amount": cart_total,
        "currency": "NGN",
        "redirect_url": redirect_url,
        'customer': {
            "email": cart.customer.email,
            "phone_number": cart.customer.phone_number,
        },
        "customizations": {
                            "title": "Tryb3 foods",
        }
    }

'''

@require_POST
@csrf_exempt
def webhook(request):
    secret_hash = os.getenv("FLW_SECRET_HASH")
    signature = request.headers.get("verifi-hash")
    if signature == None or (signature != secret_hash):
        # This request isn't from Flutterwave; discard
        return HttpResponse(status=401)
    payload = request.body
    # It's a good idea to log all received events.
    log(payload)
    # Do something (that doesn't take too long) with the payload
    return HttpResponse(status=200)

'''
