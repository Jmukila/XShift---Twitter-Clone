from flask import Blueprint, request
from app.services.auth_service import(signup_user,login_user,refresh_token)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    return signup_user(request)
    
@auth_bp.route('/login', methods=['POST'])
def login():
    return login_user(request)    

@auth_bp.route('/refresh-token',methods=['POST'])
def refresh():
    return refresh_token(request)
