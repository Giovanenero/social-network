from flask import Flask
from app.controllers.youtube_controller import youtube_bp
from app.controllers.instagram_controller import instagram_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(youtube_bp, url_prefix='/youtube')
    app.register_blueprint(instagram_bp, url_prefix='/instagram')
    
    return app
