from flask import Flask
from flask_cors import CORS
from .extensions import db
from .routes import main

def create_app():
    app = Flask(__name__)

    # Database config (VERY IMPORTANT)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)

    db.init_app(app)   # 🔥 THIS LINE FIXES YOUR ERROR

    app.register_blueprint(main)

    return app