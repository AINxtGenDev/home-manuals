#!/usr/bin/env python3
"""Development server entry point."""

import os
from app import create_app

if __name__ == "__main__":
    # Set development environment
    os.environ.setdefault("FLASK_ENV", "development")

    # Create app instance
    app = create_app("development")

    # Run development server
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=True
    )
