from app.utils.jwt_handler import getEmail
from flask import current_app,jsonify

def updates_user(request):
    db=current_app.db
    email=getEmail(request)
    if email is not None:
        try:
            users=db.collection('users').where('email','==',email).get()

            if not users:
                return jsonify({"message":"User Not Found"}),404
            user_doc=users[0]
            user_doc_ref = user_doc.reference  
            users = user_doc.to_dict()

            if users.get('isDeleted'):
                return jsonify({"message":"User Not Found"}),404
            # print("Users",users)
            data=request.json
            update_data={}

            if data.get("username") is not None:
                update_data["username"] = data["username"]
            if data.get("bio") is not None:
                update_data["bio"] = data["bio"]

            if update_data:
                user_doc_ref.update(update_data)
                # print("users",users)
                return jsonify({"message": "User updated successfully"}), 200
            else:
                return jsonify({"message": "No fields to update"}), 400
        except Exception as e:
            # print("Error while updating user:", e)
            return jsonify({"message": "Internal Server Error"}), 500

def deletes_user(request):   
    db=current_app.db
    email=getEmail(request)
    users=db.collection('users').where('email','==',email).get()
    if not users:
        return jsonify({"message":"User not Found"}),404
    user_doc=users[0]
    user_data=user_doc.reference
    users=user_doc.to_dict()
    if users.get('isDeleted'):
        return jsonify({"message":"User already deleted"}),404
    users['isDeleted']=True
    user_data.update(users)
    db.collection('tokens').document(email).delete()
    return jsonify({"message":"User Deleted Successfully"}),200
    

def search_users_with_name(name):
    db = current_app.db

    users = db.collection('users').where('username', '==', name).get()

    if not users:
        return jsonify({"message": f"User with name - {name} not found"}), 404

    user_details = []
    for user in users:
        user_data = user.to_dict()
        created_at = user_data.get("createdAt")

        user_details.append({
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "bio": user_data.get("bio"),
            "active from": created_at.year if created_at else "Unknown"
        })

    return jsonify({"Users": user_details}), 200
    
def search_users_by_id(id):
    db=current_app.db
    users=db.collection('users').document(id).get()
    users=users.to_dict()
    # print(users)
    if users is None:
        return jsonify({"message":"User Not Found"}),404
    if users.get('isDeleted'):
        return jsonify({"message":"Login Again to Continue"}),401
    user_data=[]
    user_data.append({
        "username": users.get("username"),
        "email": users.get("email"),
        "bio": users.get("bio"),
        "active from": users.get("createdAt").year 
    })
    return jsonify({"User Details":user_data}),200
