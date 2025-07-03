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
    try:
        email = getEmail(request)
        token_doc = db.collection('tokens').document(email).get()
        if not token_doc.exists:
            raise jwt.InvalidTokenError("User logged out or token invalidated")
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
