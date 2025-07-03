import datetime
from flask import jsonify,current_app
from app.utils.jwt_handler import getEmail

def create_post(request):
    db=current_app.db
    email=getEmail(request)
    user_query = db.collection('users').where('email', '==', email)
    if not user_query:
        return jsonify({"message": "User not found"}), 404
    print("email:", email)

    user_doc = user_query[0]
    user_ref= user_doc.reference
    print("User Reference:", user_ref)
    user_data = user_ref.to_dict()
    user_id = user_data.get('user_id')

    if request.json.get('content') is None:
        return jsonify({"message":"Content is required"}), 400
    post_ref=db.collection('posts').document()
    post_id=post_ref.id
    post_data = {
        'id': post_id,
        'content': request.json.get('content'),
        'author_email': email,
        'user_id': user_id,
        'created_at': datetime.datetime.utcnow()
    }
    post_ref.set(post_data)
    return jsonify({"message": "Post created successfully", "post_id": post_id}), 201

