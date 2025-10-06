"""Full-text search utilities using SQLite FTS5."""

from typing import List, Optional, Tuple

from sqlalchemy import text

from app import db
from app.models import Manual


def index_manual(manual_id: int, content: str):
    """Index a manual for full-text search.

    Args:
        manual_id: ID of the manual
        content: Text content to index
    """
    # The FTS5 triggers handle indexing automatically
    # This function is kept for explicit re-indexing if needed
    db.session.execute(
        text("INSERT OR REPLACE INTO manual_index(rowid, content_text) VALUES (:id, :content)"),
        {"id": manual_id, "content": content or ""},
    )
    db.session.commit()


def search_manuals(
    query: str,
    brand: Optional[str] = None,
    room: Optional[str] = None,
    device_type: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
) -> Tuple[List[Manual], int]:
    """Search manuals using FTS5 full-text search.

    Args:
        query: Search query string
        brand: Optional brand filter
        room: Optional room filter
        device_type: Optional device type filter
        page: Page number (1-indexed)
        per_page: Results per page

    Returns:
        Tuple of (list of Manual objects, total count)
    """
    # Start with FTS5 search
    fts_query = text(
        """
        SELECT manuals.id, manual_index.rank
        FROM manuals
        JOIN manual_index ON manuals.id = manual_index.rowid
        WHERE manual_index MATCH :query
        ORDER BY manual_index.rank
        """
    )

    # Execute FTS5 query to get matching IDs
    result = db.session.execute(fts_query, {"query": query})
    matching_ids = [row[0] for row in result]

    if not matching_ids:
        return [], 0

    # Build filtered query
    filtered_query = Manual.query.filter(Manual.id.in_(matching_ids))

    # Apply filters
    if brand:
        filtered_query = filtered_query.filter(Manual.brand == brand)
    if room:
        filtered_query = filtered_query.filter(Manual.room == room)
    if device_type:
        filtered_query = filtered_query.filter(Manual.device_type == device_type)

    # Get total count
    total = filtered_query.count()

    # Apply pagination and preserve FTS5 ranking
    manuals = (
        filtered_query.order_by(
            db.case(
                {id: index for index, id in enumerate(matching_ids)},
                value=Manual.id,
            )
        )
        .limit(per_page)
        .offset((page - 1) * per_page)
        .all()
    )

    return manuals, total


def reindex_all_manuals():
    """Rebuild the FTS5 index for all manuals."""
    # Clear existing index
    db.session.execute(text("DELETE FROM manual_index"))

    # Reindex all manuals
    manuals = Manual.query.all()
    for manual in manuals:
        if manual.content_excerpt:
            index_manual(manual.id, manual.content_excerpt)

    db.session.commit()


def get_search_filters():
    """Get available filter options for search.

    Returns:
        Dictionary with lists of unique brands, rooms, and device types
    """
    brands = (
        db.session.query(Manual.brand)
        .filter(Manual.brand.isnot(None))
        .distinct()
        .order_by(Manual.brand)
        .all()
    )

    rooms = (
        db.session.query(Manual.room)
        .filter(Manual.room.isnot(None))
        .distinct()
        .order_by(Manual.room)
        .all()
    )

    device_types = (
        db.session.query(Manual.device_type)
        .filter(Manual.device_type.isnot(None))
        .distinct()
        .order_by(Manual.device_type)
        .all()
    )

    return {
        "brands": [b[0] for b in brands],
        "rooms": [r[0] for r in rooms],
        "device_types": [d[0] for d in device_types],
    }
