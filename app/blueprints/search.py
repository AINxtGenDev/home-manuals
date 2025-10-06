"""Search blueprint."""

from flask import Blueprint, current_app, redirect, render_template, request, url_for
from flask_login import login_required

from app.forms import SearchForm
from app.search_utils import get_search_filters, search_manuals

bp = Blueprint("search", __name__, url_prefix="/search")


@bp.route("/")
@login_required
def index():
    """Search page with filters."""
    form = SearchForm()
    filters = get_search_filters()

    return render_template(
        "search/index.html",
        form=form,
        brands=filters["brands"],
        rooms=filters["rooms"],
        device_types=filters["device_types"],
    )


@bp.route("/results")
@login_required
def results():
    """Search results page."""
    query = request.args.get("query", "").strip()

    if not query:
        return redirect(url_for("search.index"))

    # Get filter parameters
    brand = request.args.get("brand") or None
    room = request.args.get("room") or None
    device_type = request.args.get("device_type") or None
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["SEARCH_RESULTS_PER_PAGE"]

    # Perform search
    manuals, total = search_manuals(
        query=query,
        brand=brand,
        room=room,
        device_type=device_type,
        page=page,
        per_page=per_page,
    )

    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page

    # Get filter options
    filters = get_search_filters()

    return render_template(
        "search/results.html",
        query=query,
        manuals=manuals,
        total=total,
        page=page,
        total_pages=total_pages,
        per_page=per_page,
        brands=filters["brands"],
        rooms=filters["rooms"],
        device_types=filters["device_types"],
        current_brand=brand,
        current_room=room,
        current_device_type=device_type,
    )
