"""Flask application factory."""

import logging
import os
from pathlib import Path

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Load config
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    from app.config import config

    app.config.from_object(config[config_name])

    # Ensure instance and storage directories exist
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.config["STORAGE_DIR"].mkdir(parents=True, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User

        return User.query.get(int(user_id))

    # Configure logging
    setup_logging(app)

    # Register security middleware
    from app.security import register_security_headers

    register_security_headers(app)

    # Register blueprints
    from app.blueprints import auth, manuals, search

    app.register_blueprint(auth.bp)
    app.register_blueprint(manuals.bp)
    app.register_blueprint(search.bp)

    # Register CLI commands
    from app import cli

    cli.init_app(app)

    # Index route
    @app.route("/")
    def index():
        from flask import redirect, url_for

        return redirect(url_for("manuals.list_manuals"))

    return app


def setup_logging(app):
    """Configure structured logging."""
    log_level = logging.DEBUG if app.config.get("DEBUG") else logging.INFO

    # Console handler with JSON formatting for production
    handler = logging.StreamHandler()
    handler.setLevel(log_level)

    if not app.config.get("DEBUG"):
        # JSON format for production
        formatter = logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}'
        )
    else:
        # Human-readable format for development
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)
