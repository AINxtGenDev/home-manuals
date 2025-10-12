"""Test configuration and fixtures."""

import os
import tempfile

import pytest

from app import create_app, db
from app.models import Manual, User


@pytest.fixture(scope="session")
def app():
    """Create application for the tests."""
    # Create a temporary directory for test storage
    storage_dir = tempfile.mkdtemp()

    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()

    app = create_app("testing")
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
        "STORAGE_DIR": storage_dir,
    })

    # Create the database and the database table
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="function")
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def _db(app):
    """A database for the tests."""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def test_user(app, _db):
    """Create a test user."""
    user = User(email="test@example.com")
    user.set_password("testpassword123")
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture(scope="function")
def test_manual(app, _db, test_user):
    """Create a test manual."""
    manual = Manual(
        title="Test Manual",
        brand="TestBrand",
        model="Model123",
        room="Living Room",
        device_type="TV",
        year=2023,
        file_path="test.pdf",
        file_hash="test123hash",
        file_size=1024,
        pages=10,
        owner_id=test_user.id,
    )
    _db.session.add(manual)
    _db.session.commit()
    return manual


@pytest.fixture(scope="function")
def authenticated_client(client, test_user):
    """Return a client with an authenticated user."""
    with client:
        with client.session_transaction() as session:
            session["_user_id"] = str(test_user.id)
            session["_fresh"] = True
    return client
