from flask import request, jsonify, current_app
import datetime
import jwt
from firebase_admin import auth as firebase_auth
from app.utils.jwt_handler import encodeJWT
from werkzeug.security import generate_password_hash, check_password_hash 


def signup_user(data):
    db = current_app.db
    data = request.json
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')
    hash_password = generate_password_hash(password)

    if not email or not password or not username:
        return jsonify({'message': 'Missing fields'}), 400

    try:
        # 1. Create user in Firebase Auth
        user_record = firebase_auth.create_user(
            email=email,
            password=password
        )
        user_id= user_record.uid
        # 2. Store user info in Firestore
        user_ref = db.collection('users').document(user_id)
        user_ref.set({
            'user_id': user_id,
            'username': username,
            'email': email,
            'password': hash_password,
            'bio':"Hi I am new here",
            'isDeleted':False,
            'createdAt': datetime.datetime.utcnow()
        })

        return jsonify({'message': 'User created successfully', 'userId': user_id}), 200

    except Exception as e:
        return jsonify({'message': 'Error creating user', 'error': str(e)}), 500


def login_user(request):
    db = current_app.db
    data = request.json

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400

    try:
        # Step 1: Find user by email
        users = db.collection('users').where("email", "==", email).get()

        if not users:
            return jsonify({'message': 'User not found'}), 404

        user_doc = users[0]
        user_data = user_doc.to_dict()


        user_data["isDeleted"]=False
        user_doc.reference.update(user_data)
        print("In Auth ",user_data)     
        # Step 2: Check password using check_password_hash
        print(check_password_hash(user_data['password'], password))

        if not check_password_hash(user_data['password'], password):
            return jsonify({'message': 'Invalid password'}), 401

        # Step 3: Create JWT access token (valid 10 minutes)
        payload_dict={
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        }

        access_token = encodeJWT(payload_dict)

        refresh_payload={
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }
        refresh_token=encodeJWT(refresh_payload)

        
        # Store tokens in the Firestore db 
        db.collection('tokens').document(email).set({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'access_exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
        'refresh_exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        'createdAt': datetime.datetime.utcnow()
    })

        print("Stored Successfully in the DB")

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token':refresh_token
        }), 200

    except Exception as e:
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500


def refresh_token(request):

    db=current_app.db
    data=request.json
    email=data.get('email')
    refresh_token=data.get('refresh_token')

    token_data_ref = db.collection('tokens').document(email)
    
    token_snapshot = token_data_ref.get()
    token_data=token_snapshot.to_dict()
    if token_data is None:
        return jsonify({"message":"Login Again..User Logged out"}),401
    
    # Check if refresh token matches the db stored
    if token_data['refresh_token'] != refresh_token:
        return jsonify({'message': 'Invalid refresh token'}), 401
    


    refresh_exp = token_data['refresh_exp'].replace(tzinfo=None)

    if datetime.datetime.utcnow() > refresh_exp:
        db.collection('tokens').document(email).delete()
        return jsonify({'message': 'Refresh token expired. Please login again.'}), 401

    access_exp = token_data['access_exp'].replace(tzinfo=None)
    if datetime.datetime.utcnow() < access_exp:
        return jsonify({
            "message": "Access Token Still valid. No need new one",
            "access_token": token_data['access_token'],
            "access_exp": token_data['access_exp'].isoformat()  
        }), 200
    
    # Generate new access token
    try:

        new_exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        payload_dict={
            'email':email,
            'access_exp':new_exp.isoformat() 
        }

        access_token=encodeJWT(payload_dict)

        db.collection('tokens').document(email).update({
            'access_token': access_token,
            'access_exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        })
        return jsonify({
            "message": "New access token issued",
            "access_token": access_token,
            "access_exp": new_exp.isoformat()  
        }), 200
    
    except jwt.InvalidTokenError:
        return jsonify({"message":"Token Invalid Login Again"})


