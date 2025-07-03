from flask import Flask,request
from firebase_admin import credentials, firestore, initialize_app
import firebase_admin

from app.utils.jwt_handler import authentication

def create_app():

     
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'

    # Firebase Init
    if not firebase_admin._apps:
        cred = credentials.Certificate('firebase/firebase_config.json')
        initialize_app(cred)

    app.db = firestore.client()

    @app.before_request
    def check_token():
        if request.path in ["/login", "/signup", "/refresh-token"]:
           return 
        return authentication(request)
       
    # Register Auth Routes
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp)

    from app.routes.post_routes import post_bp
    app.register_blueprint(post_bp)
    
    return app

