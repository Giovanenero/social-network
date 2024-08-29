from flask import Flask
from app.controllers.youtube_controller import youtube_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(youtube_bp, url_prefix='/youtube')
    
    return app
