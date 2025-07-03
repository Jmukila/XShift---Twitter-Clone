from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from firebase_admin import auth as firebase_auth
from app.services.user_service import (search_users_with_name, search_users_by_id, updates_user, deletes_user)

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/updateuser',methods=['POST'])
def update_user():
    return updates_user(request)
    
@user_bp.route('/user/deleteuser', methods=['POST'])
def delete_user():
    return deletes_user(request)


@user_bp.route('/user/searchuser/<name>', methods=['GET'])
def search_user_with_name(name):
    return search_users_with_name(name)

@user_bp.route('/user/searchuserbyid/<id>', methods=['GET'])
def search_user_by_id(id):
    return  search_users_by_id(id)