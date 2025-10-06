"""Flask CLI commands."""

import click
from flask import Flask

from app import db
from app.models import User
from app.search_utils import reindex_all_manuals


def init_app(app: Flask):
    """Register CLI commands with the Flask app."""

    @app.cli.command("create-admin")
    @click.option("--email", prompt=True, help="Admin email address")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin(email, password):
        """Create an admin user."""
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            click.echo(f"Error: User with email '{email}' already exists.", err=True)
            return

        # Create new admin user
        user = User(email=email, is_admin=True)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        click.echo(f"✓ Admin user '{email}' created successfully!")

    @app.cli.command("init-db")
    def init_db():
        """Initialize the database."""
        db.create_all()
        click.echo("✓ Database initialized!")

    @app.cli.command("reindex")
    def reindex():
        """Rebuild the full-text search index."""
        click.echo("Reindexing all manuals...")
        reindex_all_manuals()
        click.echo("✓ Reindexing complete!")
