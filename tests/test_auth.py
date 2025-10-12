"""Tests for authentication functionality."""


from app.models import User


class TestAuthRoutes:
    """Test cases for authentication routes."""

    def test_app_exists(self, app):
        """Test that the application exists."""
        assert app is not None

    def test_app_is_testing(self, app):
        """Test that the app is in testing mode."""
        assert app.config["TESTING"]

    def test_csrf_disabled_in_testing(self, app):
        """Test that CSRF is disabled in testing."""
        assert not app.config["WTF_CSRF_ENABLED"]


class TestUserAuthentication:
    """Test cases for user authentication."""

    def test_user_can_set_password(self, app, _db):
        """Test that a user can set a password."""
        user = User(email="test@example.com")
        user.set_password("securepassword")

        assert user.password_hash is not None
        assert user.password_hash != "securepassword"

    def test_user_can_verify_password(self, app, test_user):
        """Test that a user can verify their password."""
        assert test_user.check_password("testpassword123")
        assert not test_user.check_password("wrongpassword")

    def test_password_verification_fails_with_wrong_password(self, app, test_user):
        """Test that password verification fails with wrong password."""
        assert not test_user.check_password("incorrectpassword")

    def test_password_hash_is_different_for_same_password(self, app, _db):
        """Test that password hashes are different even for the same password."""
        user1 = User(email="user1@example.com")
        user1.set_password("samepassword")

        user2 = User(email="user2@example.com")
        user2.set_password("samepassword")

        assert user1.password_hash != user2.password_hash
