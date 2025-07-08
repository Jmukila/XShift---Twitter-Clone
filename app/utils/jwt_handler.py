import datetime
from flask import current_app, jsonify
import jwt


def getEmail(request):
    bearer = request.headers.get('Authorization')
    if not bearer or not bearer.startswith("Bearer "):
        raise jwt.InvalidTokenError("Missing or invalid token")

    token = bearer[7:]
    if token is None:
        raise jwt.InvalidTokenError("Missing token")
    try:
        return decodeJWT(token)
    except Exception as e:
        raise jwt.InvalidTokenError("Invalid token")

def encodeJWT(payload_dict):
    return jwt.encode(payload_dict, current_app.config['SECRET_KEY'], algorithm='HS256')

def decodeJWT(token):
    email= jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    print("Email Helloo      ",email['email'])
    return email['email']

def authentication(request):
    db = current_app.db
    data=request.json
    print("Data: ",data)
    print("Data in auth:",data)
    try:
        email = getEmail(request)
        token_data_ref = db.collection('tokens').document(email)
        token_snapshot = token_data_ref.get()
        token_data=token_snapshot.to_dict()
        if token_data is None:
            return jsonify({"message":"Login Again..User Logged out"}),401
        access_exp = token_data['access_exp'].replace(tzinfo=None)

        if datetime.datetime.utcnow() > access_exp:
            db.collection('tokens').document(email).delete()
            return jsonify({'message': 'Token expired...Log In Again'}), 401
        if datetime.datetime.utcnow() > access_exp:
            return jsonify({'message': 'Access Token expired.Try Refresh Token generating'}), 401
        return None
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token Expired"}), 401
    except jwt.InvalidTokenError as e:
        # Customize message based on error detail
        error_msg = str(e)
        if "Missing or invalid token" in error_msg:
            return jsonify({"message": "Missing token"}), 401
        elif "User logged out" in error_msg:
            return jsonify({"message": "Token invalidated"}), 401
        return jsonify({"message": "Invalid token"}), 401
