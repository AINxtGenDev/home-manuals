"""Manuals blueprint."""

import uuid
from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user, login_required

from app import db
from app.forms import ManualUploadForm
from app.models import Manual, ReadingProgress
from app.pdf_utils import compute_file_hash, extract_pdf_text, validate_pdf_file

bp = Blueprint("manuals", __name__, url_prefix="/manuals")


@bp.route("/")
def index():
    """Redirect to list view."""
    return redirect(url_for("manuals.list_manuals"))


@bp.route("/list")
@login_required
def list_manuals():
    """List all manuals with pagination and filtering."""
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["MANUALS_PER_PAGE"]

    # Get filter parameters
    brand = request.args.get("brand")
    room = request.args.get("room")
    device_type = request.args.get("device_type")
    sort_by = request.args.get("sort", "uploaded_at")

    # Build query
    query = Manual.query

    # Apply filters
    if brand:
        query = query.filter_by(brand=brand)
    if room:
        query = query.filter_by(room=room)
    if device_type:
        query = query.filter_by(device_type=device_type)

    # Apply sorting
    if sort_by == "title":
        query = query.order_by(Manual.title.asc())
    elif sort_by == "brand":
        query = query.order_by(Manual.brand.asc())
    else:  # default: uploaded_at
        query = query.order_by(Manual.uploaded_at.desc())

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Get filter options
    all_brands = (
        db.session.query(Manual.brand)
        .filter(Manual.brand.isnot(None))
        .distinct()
        .order_by(Manual.brand)
        .all()
    )
    all_rooms = (
        db.session.query(Manual.room)
        .filter(Manual.room.isnot(None))
        .distinct()
        .order_by(Manual.room)
        .all()
    )
    all_device_types = (
        db.session.query(Manual.device_type)
        .filter(Manual.device_type.isnot(None))
        .distinct()
        .order_by(Manual.device_type)
        .all()
    )

    return render_template(
        "manuals/list.html",
        pagination=pagination,
        manuals=pagination.items,
        brands=[b[0] for b in all_brands],
        rooms=[r[0] for r in all_rooms],
        device_types=[d[0] for d in all_device_types],
        current_brand=brand,
        current_room=room,
        current_device_type=device_type,
        current_sort=sort_by,
    )


@bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Upload a new manual."""
    form = ManualUploadForm()

    if form.validate_on_submit():
        file = form.file.data

        # Validate file extension
        if not file.filename.lower().endswith(".pdf"):
            flash("Only PDF files are allowed.", "danger")
            return redirect(url_for("manuals.upload"))

        # Generate UUID filename
        file_uuid = uuid.uuid4().hex
        dest_path = current_app.config["STORAGE_DIR"] / f"{file_uuid}.pdf"

        # Save file temporarily
        file.save(dest_path)

        # Validate PDF
        if not validate_pdf_file(dest_path):
            dest_path.unlink()
            flash("Invalid PDF file.", "danger")
            return redirect(url_for("manuals.upload"))

        # Check file size
        file_size = dest_path.stat().st_size
        max_size = current_app.config["MAX_CONTENT_LENGTH"]
        if file_size > max_size:
            dest_path.unlink()
            flash(
                f"File too large (max {current_app.config['MAX_FILE_SIZE_MB']}MB).",
                "danger",
            )
            return redirect(url_for("manuals.upload"))

        # Compute hash and check for duplicates
        file_hash = compute_file_hash(dest_path)
        existing_manual = Manual.query.filter_by(file_hash=file_hash).first()

        if existing_manual:
            dest_path.unlink()
            flash(
                f"This file already exists: {existing_manual.title}",
                "warning",
            )
            return redirect(url_for("manuals.detail", id=existing_manual.id))

        # Extract text
        num_pages, full_text = extract_pdf_text(dest_path)
        excerpt = full_text[:500] if full_text else None

        # Create manual record
        manual = Manual(
            title=form.title.data,
            brand=form.brand.data or None,
            model=form.model.data or None,
            device_type=form.device_type.data or None,
            room=form.room.data or None,
            year=form.year.data,
            tags=form.tags.data or None,
            file_path=str(dest_path),
            file_hash=file_hash,
            file_size=file_size,
            pages=num_pages,
            content_excerpt=excerpt,
            owner_id=current_user.id,
        )

        db.session.add(manual)
        db.session.commit()

        current_app.logger.info(
            f"Manual uploaded: {manual.title} (ID: {manual.id}) by {current_user.email}"
        )
        flash(f'Manual "{manual.title}" uploaded successfully!', "success")
        return redirect(url_for("manuals.detail", id=manual.id))

    return render_template("manuals/upload.html", form=form)


@bp.route("/<int:id>")
@login_required
def detail(id):
    """View manual details and PDF."""
    manual = Manual.query.get_or_404(id)

    # Get or create reading progress
    progress = ReadingProgress.query.filter_by(
        manual_id=manual.id, user_id=current_user.id
    ).first()

    current_page = progress.page if progress else 1

    return render_template(
        "manuals/detail.html",
        manual=manual,
        current_page=current_page,
    )


@bp.route("/files/<filename>")
@login_required
def serve_file(filename):
    """Serve a PDF file."""
    file_path = current_app.config["STORAGE_DIR"] / filename

    if not file_path.exists():
        flash("File not found.", "danger")
        return redirect(url_for("manuals.list_manuals"))

    return send_file(file_path, mimetype="application/pdf")


@bp.route("/progress/<int:manual_id>", methods=["POST"])
@login_required
def update_progress(manual_id):
    """Update reading progress (AJAX endpoint)."""
    manual = Manual.query.get_or_404(manual_id)
    page = request.json.get("page", 1)

    # Get or create progress record
    progress = ReadingProgress.query.filter_by(
        manual_id=manual.id, user_id=current_user.id
    ).first()

    if progress:
        progress.page = page
    else:
        progress = ReadingProgress(manual_id=manual.id, user_id=current_user.id, page=page)
        db.session.add(progress)

    db.session.commit()

    return {"status": "success", "page": page}
