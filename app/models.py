"""Database models."""

from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Index, event
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class User(UserMixin, db.Model):
    """User model for authentication."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    manuals = db.relationship("Manual", back_populates="owner", lazy="dynamic")
    reading_progress = db.relationship(
        "ReadingProgress", back_populates="user", lazy="dynamic", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        """Hash and set the user password."""
        self.password_hash = generate_password_hash(password, method="scrypt")

    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


class Manual(db.Model):
    """Manual model for PDF documents."""

    __tablename__ = "manuals"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    brand = db.Column(db.String(100), nullable=True, index=True)
    model = db.Column(db.String(100), nullable=True)
    device_type = db.Column(db.String(50), nullable=True, index=True)
    room = db.Column(db.String(50), nullable=True, index=True)
    year = db.Column(db.Integer, nullable=True)
    tags = db.Column(db.String(200), nullable=True)  # comma-separated
    file_path = db.Column(db.String(500), unique=True, nullable=False)
    file_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    file_size = db.Column(db.Integer, nullable=False)
    pages = db.Column(db.Integer, nullable=True)
    thumbnail_path = db.Column(db.String(500), nullable=True)
    content_excerpt = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Relationships
    owner = db.relationship("User", back_populates="manuals")
    reading_progress = db.relationship(
        "ReadingProgress", back_populates="manual", lazy="dynamic", cascade="all, delete-orphan"
    )

    def get_tags_list(self):
        """Return tags as a list."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    def __repr__(self):
        return f"<Manual {self.title}>"


class ManualIndex(db.Model):
    """FTS5 virtual table for full-text search."""

    __tablename__ = "manual_index"

    # FTS5 virtual table - will be created via raw SQL
    # This model is primarily for reference
    rowid = db.Column(db.Integer, primary_key=True)
    content_text = db.Column(db.Text, nullable=False)

    __table_args__ = (
        {
            "info": {
                "is_fts5": True,
                "fts_columns": ["content_text"],
            }
        },
    )


class ReadingProgress(db.Model):
    """Track reading progress for each manual per user."""

    __tablename__ = "reading_progress"

    id = db.Column(db.Integer, primary_key=True)
    manual_id = db.Column(db.Integer, db.ForeignKey("manuals.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    page = db.Column(db.Integer, default=1, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    manual = db.relationship("Manual", back_populates="reading_progress")
    user = db.relationship("User", back_populates="reading_progress")

    __table_args__ = (
        db.UniqueConstraint("manual_id", "user_id", name="uq_manual_user"),
        Index("idx_reading_progress_user", "user_id"),
    )

    def __repr__(self):
        return f"<ReadingProgress manual={self.manual_id} user={self.user_id} page={self.page}>"


# Event listener to create FTS5 virtual table
@event.listens_for(Manual.__table__, "after_create")
def create_fts5_table(target, connection, **kw):
    """Create FTS5 virtual table after Manual table is created."""
    connection.execute(
        db.text(
            """
        CREATE VIRTUAL TABLE IF NOT EXISTS manual_index
        USING fts5(content_text, content=manuals, content_rowid=id)
        """
        )
    )

    # Create triggers to keep FTS5 in sync
    connection.execute(
        db.text(
            """
        CREATE TRIGGER IF NOT EXISTS manuals_ai AFTER INSERT ON manuals BEGIN
            INSERT INTO manual_index(rowid, content_text)
            VALUES (new.id, COALESCE(new.content_excerpt, ''));
        END
        """
        )
    )

    connection.execute(
        db.text(
            """
        CREATE TRIGGER IF NOT EXISTS manuals_ad AFTER DELETE ON manuals BEGIN
            DELETE FROM manual_index WHERE rowid = old.id;
        END
        """
        )
    )

    connection.execute(
        db.text(
            """
        CREATE TRIGGER IF NOT EXISTS manuals_au AFTER UPDATE ON manuals BEGIN
            UPDATE manual_index SET content_text = COALESCE(new.content_excerpt, '')
            WHERE rowid = new.id;
        END
        """
        )
    )
