from flask import Flask
from .extensions import db, migrate, jwt
from .config import DevConfig
from .api.auth_routes import auth_bp
from .api.task_routes import task_bp

def create_app(config_class=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(task_bp, url_prefix="/tasks")

    return app
