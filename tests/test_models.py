"""Tests for database models."""

from datetime import datetime

import pytest

from app.models import Manual, User


class TestUserModel:
    """Test cases for User model."""

    def test_create_user(self, app, _db):
        """Test creating a new user."""
        user = User(email="new@example.com")
        user.set_password("password123")

        _db.session.add(user)
        _db.session.commit()

        assert user.id is not None
        assert user.email == "new@example.com"
        assert user.password_hash is not None
        assert user.password_hash != "password123"

    def test_password_hashing(self, app, _db):
        """Test password hashing and verification."""
        user = User(email="test@example.com")
        user.set_password("mypassword")

        assert user.check_password("mypassword")
        assert not user.check_password("wrongpassword")

    def test_user_repr(self, app, test_user):
        """Test user string representation."""
        assert repr(test_user) == "<User test@example.com>"

    def test_unique_email(self, app, _db, test_user):
        """Test that emails must be unique."""
        from sqlalchemy.exc import IntegrityError

        user2 = User(email="test@example.com")
        user2.set_password("password")

        _db.session.add(user2)

        with pytest.raises(IntegrityError):
            _db.session.commit()


class TestManualModel:
    """Test cases for Manual model."""

    def test_create_manual(self, app, _db, test_user):
        """Test creating a new manual."""
        manual = Manual(
            title="New Manual",
            brand="Brand",
            model="Model",
            file_path="new_test.pdf",
            file_hash="newhash123",
            file_size=2048,
            owner_id=test_user.id
        )

        _db.session.add(manual)
        _db.session.commit()

        assert manual.id is not None
        assert manual.title == "New Manual"
        assert manual.brand == "Brand"
        assert manual.model == "Model"
        assert manual.owner_id == test_user.id

    def test_manual_repr(self, app, test_manual):
        """Test manual string representation."""
        assert repr(test_manual) == "<Manual Test Manual>"

    def test_manual_relationships(self, app, test_manual, test_user):
        """Test manual relationships with user."""
        assert test_manual.owner == test_user
        assert test_manual in test_user.manuals.all()

    def test_manual_timestamps(self, app, test_manual):
        """Test manual timestamp fields."""
        assert test_manual.created_at is not None
        assert isinstance(test_manual.created_at, datetime)
        assert test_manual.updated_at is not None
        assert isinstance(test_manual.updated_at, datetime)

    def test_manual_optional_fields(self, app, _db, test_user):
        """Test manual with optional fields."""
        manual = Manual(
            title="Complete Manual",
            brand="TestBrand",
            model="Model123",
            room="Kitchen",
            device_type="Appliance",
            year=2023,
            pages=50,
            tags="warranty,manual,guide",
            file_path="complete.pdf",
            file_hash="completehash456",
            file_size=5120,
            owner_id=test_user.id
        )

        _db.session.add(manual)
        _db.session.commit()

        assert manual.room == "Kitchen"
        assert manual.device_type == "Appliance"
        assert manual.year == 2023
        assert manual.pages == 50
        assert manual.tags == "warranty,manual,guide"
