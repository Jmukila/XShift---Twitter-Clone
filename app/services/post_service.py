import datetime
from flask import jsonify,current_app
from app.utils.jwt_handler import getEmail

def create_post(request):
    db=current_app.db
    email=getEmail(request)
    users=db.collection('users').where('email','==',email).get()
    if not users:
        return jsonify({"message": "User not found"}), 404
    
    user_doc=users[0]
    users=user_doc.to_dict()
    user_id = users.get('user_id')

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
    return jsonify({"message": "Post created successfully"}), 201

def edit_post(request,id):
    db=current_app.db
    email=getEmail(request)
    users=db.collection('users').where('email','==',email).get()
    if not users:
        return jsonify({"message": "User not found"}), 404
    
    posts=db.collection('posts').document(id).get()
    if not posts.exists:
        return jsonify({"message":"Post Doesn't exist"})
    
    posts_dict=posts.to_dict()

    if posts_dict.get('author_email')!=email:
        return jsonify({"message":"Only the User can update the they create post"}) 
       
    if request.json.get('content') is None:
        return jsonify({"message":"Content is required"}), 400
    post_ref=db.collection('posts').document(id)
    post_data = {
        'content': request.json.get('content'),
        'created_at': datetime.datetime.utcnow()
    }
    post_ref.update(post_data)
    return jsonify({"message": "Post Updated successfully"}), 200
