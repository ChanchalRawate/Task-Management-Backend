import os
from flask import Flask
from .extensions import db, jwt
from .routes import main
from config import DevConfig  # make sure config.py is at the root

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(DevConfig)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    app.register_blueprint(main)

    # Create DB if missing
    with app.app_context():
        db.create_all()

    print("Running with DevConfig (SQLite)")
    return app
