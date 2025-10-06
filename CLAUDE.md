# CLAUDE.md — House Manuals (Flask) Assistant Guide

You are an expert **Senior Full‑Stack Developer** and **Security Engineer** assisting with the development of *House Manuals*, a Python **Flask** web application that lets the user **ingest, organize, and read household user manuals (PDFs)** with a **mobile-first, highly readable** browser UI (HTML/CSS/JS).

**CRITICAL**: This app will be used **primarily on mobile devices** (phones/tablets). Reading PDFs and navigating the UI must be **exceptionally readable and usable** on small screens. Prioritize mobile UX over desktop in all design decisions.

Your outputs must be production‑ready, precise, and follow best practices. Provide complete code when asked to generate files, prefer small iterative PR‑sized changes, and explain the *why* behind decisions.

---

## Project Goals

1. **Mobile-First Readability**: Large, readable fonts (min 16px base); high contrast; touch-friendly buttons (min 44px tap targets); smooth scrolling; optimized PDF rendering on small screens.
2. **Upload & Store**: Accept PDF manuals (max 50MB); persist metadata in DB; store files on disk with UUID naming; detect duplicates via file hash.
3. **Search & Browse**: Full‑text search (SQLite FTS5) with filters (brand, device type, room, tags); paginated results; large search input; instant results on mobile.
4. **View & Read**: Mobile-optimized PDF viewer (PDF.js) with:
   - Single-column layout on mobile
   - Pinch-to-zoom support
   - Fast page rendering
   - Progress indicator (page X of Y)
   - Remember last page read
   - Landscape mode support
5. **Extract & Index**: Parse PDFs (pypdf for text extraction) to populate FTS5 searchable index.
6. **Secure by Default**: Single admin auth (Flask-Login), CSRF protection, input validation, safe file handling, security headers, and structured logging.
7. **DevX**: Reproducible dev environment, linters (ruff), tests (pytest), Alembic migrations, Docker/Compose.

---

## Tech Stack

- **Backend**: Python 3.11+, Flask 3.x, Jinja2, SQLAlchemy 2.x (SQLite dev/prod with FTS5), Flask‑Login, Flask-WTF, python-dotenv.
- **Search**: SQLite FTS5 (built-in, fast, zero dependencies).
- **PDF**: `pypdf` for text extraction, PDF.js (frontend viewer with mobile optimizations).
- **Frontend**:
  - **Mobile-First CSS**: System font stack, fluid typography (clamp), CSS Grid/Flexbox, touch-optimized spacing
  - **Viewport**: `<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">`
  - **Typography**: Min 16px base font, 1.5 line-height, high contrast (#000 on #fff)
  - **Tap Targets**: Min 44x44px buttons/links with adequate spacing
  - **JavaScript**: Minimal ES6 (PDF.js, reading progress, search)
- **Build/Quality**: `ruff` (lint/format), `pytest`, Alembic (migrations).
- **Ops**: Docker + docker‑compose, `.env` config, Gunicorn + Nginx (prod).

---

## High-Level Architecture

```
/home-manuals              # project root
  /app
    __init__.py            # Flask app factory
    /blueprints
      auth.py              # login, logout; password hashing (Werkzeug)
      manuals.py           # upload, list, view, detail
      search.py            # search routes and filters
    models.py              # SQLAlchemy models (User, Manual, ManualIndex, ReadingProgress)
    search_utils.py        # FTS5 indexer, query helpers
    pdf_utils.py           # safe filename, text extraction, file hash
    forms.py               # Flask-WTF forms (upload, search, login)
    security.py            # Security headers middleware
    cli.py                 # Flask CLI commands (init-db, reindex, create-admin)
    config.py              # Config classes (Dev, Prod) using python-dotenv
  /instance                # SQLite DB + instance-specific config (gitignored)
  /migrations              # Alembic migration scripts
  /templates
    base.html              # Base template with nav, footer
    /auth
      login.html
    /manuals
      list.html            # Paginated list with filters
      detail.html          # PDF viewer + metadata
      upload.html
    /search
      results.html         # Search results page
  /static
    /css
      main.css             # Mobile-first styles (base 16px, fluid typography)
      viewer.css           # PDF viewer mobile optimizations
    /js
      viewer.js            # PDF.js integration (pinch-zoom, page navigation)
      progress.js          # Reading progress tracker
    /vendor
      pdf.js/              # PDF.js library (CDN or local)
  /storage                 # PDF files (gitignored; configurable path)
  /tests
    conftest.py            # pytest fixtures
    test_upload.py
    test_search.py
    test_auth.py
  requirements.txt         # Python dependencies
  requirements-dev.txt     # Dev dependencies (pytest, ruff, etc.)
  .env.example             # Example environment variables
  .env                     # Actual secrets (gitignored)
  docker-compose.yml       # Dev environment
  Dockerfile
  Makefile                 # Common tasks (dev, test, lint, db)
  pyproject.toml           # ruff config
  .gitignore
  README.md
```

---

## Data Model

```python
class User(db.Model):
    id: int (PK)
    email: str (unique, indexed)
    password_hash: str
    is_admin: bool (default True for MVP single-user)
    created_at: datetime
    last_login: datetime (nullable)

class Manual(db.Model):
    id: int (PK)
    title: str (indexed)
    brand: str (nullable, indexed)
    model: str (nullable)
    device_type: str (nullable, indexed)  # e.g., "Appliance", "Electronics"
    room: str (nullable, indexed)         # e.g., "Kitchen", "Garage"
    year: int (nullable)
    tags: str (comma-separated, nullable) # e.g., "warranty,installation"
    file_path: str (unique)               # /storage/{uuid}.pdf
    file_hash: str (unique, SHA256)       # detect duplicates
    file_size: int                        # bytes
    pages: int (nullable)
    thumbnail_path: str (nullable)        # first-page preview image
    content_excerpt: str (nullable)       # first 500 chars for preview
    uploaded_at: datetime
    created_at: datetime                  # metadata created
    updated_at: datetime
    owner_id: int (FK → User, nullable)   # always admin for MVP

class ManualIndex(db.Model):  # SQLite FTS5 virtual table
    rowid: int (→ Manual.id)
    content_text: str                     # full extracted text

class ReadingProgress(db.Model):
    id: int (PK)
    manual_id: int (FK → Manual)
    user_id: int (FK → User)
    page: int (default 1)
    updated_at: datetime
    unique constraint on (manual_id, user_id)
```

---

## Security Requirements

- **Auth**: Flask‑Login + Werkzeug password hashing (`scrypt` or `pbkdf2:sha256`).
- **CSRF**: Flask-WTF CSRF protection on all POST/PUT/DELETE routes.
- **File Uploads**:
  - Max size: 50MB (configurable).
  - Extension whitelist: `.pdf` only.
  - MIME type check + PDF magic bytes (`%PDF-`).
  - UUID-based storage naming (`{uuid4}.pdf`).
  - SHA256 hash for duplicate detection.
- **HTTP Security Headers**:
  - `Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';`
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains` (prod only)
- **Logging**: Structured JSON logs (uploads, logins, errors) with timestamps and user context.
- **Secrets**: All sensitive config in `.env` (SECRET_KEY, DB URI); never committed; .env.example provided.

---

## MVP Features

1. **Admin Login** - Large, touch-friendly login form; session-based auth; logout button in nav.
2. **Upload PDF** - Mobile-friendly form with large file picker button; metadata inputs (title, brand, model, room, tags); validate PDF; store with UUID.
3. **List Manuals** - Mobile-optimized card layout (stacked, not table); large tap targets; show title, brand, room, uploaded date; easy thumb scrolling; sort by date/title.
4. **View Manual** - Full-screen mobile PDF viewer with:
   - Large page navigation buttons (prev/next)
   - Page counter (e.g., "Page 5 of 24")
   - Pinch-to-zoom
   - Single-page mode (vertical scroll)
   - Metadata collapsible panel
   - Back button to list
5. **Full-Text Search** - Large search input (min 44px height); filter chips/dropdowns; instant results; mobile-friendly results cards.
6. **Reading Progress** - Auto-save last page viewed; resume with "Continue reading from page X" button.
7. **Duplicate Detection** - Clear mobile toast notification if uploading duplicate.
8. **Security Hardening** - CSRF tokens, security headers, input validation, structured logging.
9. **Mobile Navigation** - Hamburger menu or bottom nav bar; clear "Home", "Search", "Upload" actions.

---

## Example Upload Handler (Sketch)

```python
@bp.route('/manuals/upload', methods=['GET', 'POST'])
@login_required
def upload_manual():
    form = ManualUploadForm()
    if form.validate_on_submit():
        f = form.file.data

        # Validate extension
        if not f.filename.lower().endswith('.pdf'):
            flash('Only PDF files allowed.', 'danger')
            return redirect(url_for('.upload_manual'))

        # Validate PDF magic bytes
        header = f.read(5)
        f.seek(0)
        if header != b'%PDF-':
            flash('Invalid PDF file.', 'danger')
            return redirect(url_for('.upload_manual'))

        # Check file size (50MB)
        f.seek(0, 2)  # seek to end
        size = f.tell()
        f.seek(0)
        if size > 50 * 1024 * 1024:
            flash('File too large (max 50MB).', 'danger')
            return redirect(url_for('.upload_manual'))

        # Save with UUID naming
        uid = uuid.uuid4().hex
        dest = Path(app.config['STORAGE_DIR']) / f'{uid}.pdf'
        dest.parent.mkdir(parents=True, exist_ok=True)
        f.save(dest)

        # Hash & duplicate check
        file_hash = compute_sha256(dest)
        existing = Manual.query.filter_by(file_hash=file_hash).first()
        if existing:
            dest.unlink()  # delete duplicate
            flash(f'This file already exists: {existing.title}', 'warning')
            return redirect(url_for('.detail', id=existing.id))

        # Extract text & metadata
        pages, text = extract_pdf_text(dest)
        excerpt = text[:500] if text else None

        # Create Manual record
        m = Manual(
            title=form.title.data,
            brand=form.brand.data,
            model=form.model.data,
            room=form.room.data,
            device_type=form.device_type.data,
            tags=form.tags.data,
            file_path=str(dest),
            file_hash=file_hash,
            file_size=size,
            pages=pages,
            content_excerpt=excerpt,
            owner_id=current_user.id,
        )
        db.session.add(m)
        db.session.flush()

        # Index for FTS5 search
        index_manual(m.id, text)

        db.session.commit()
        flash(f'Manual "{m.title}" uploaded successfully.', 'success')
        return redirect(url_for('.detail', id=m.id))

    return render_template('manuals/upload.html', form=form)
```

---

## Routes (Summary)

**Auth Blueprint** (`/auth`)
- `GET  /login` → login form
- `POST /login` → authenticate user
- `GET  /logout` → logout + redirect to login

**Manuals Blueprint** (`/manuals`)
- `GET  /` → redirect to `/manuals/list`
- `GET  /list` → paginated list (query params: page, sort, brand, room)
- `GET  /upload` → upload form
- `POST /upload` → process upload + validation
- `GET  /<id>` → detail view with PDF viewer
- `GET  /files/<uuid>.pdf` → serve PDF (login required, send_file)

**Search Blueprint** (`/search`)
- `GET /` → search page with filters
- `GET /results` → FTS5 query results (query params: q, brand, room, device_type)

**API Blueprint** (`/api`) - optional AJAX endpoints
- `POST /progress` → update reading progress (JSON: {manual_id, page})

---

## Development Workflow

- **Branching**: `feature/<short-name>` from `main`
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, etc.)
- **Local Dev**: `make dev` (Flask dev server with auto-reload)
- **Database**: `make db` (Alembic migrations), `flask create-admin` (CLI command)
- **Quality**: `make lint` (ruff), `make test` (pytest with coverage)
- **Docker**: `docker-compose up` for isolated dev environment
- **CI**: GitHub Actions on push (lint, test, build Docker image)

---

## Development Phases

### Phase 1: Foundation (Days 1-2)
1. Project structure + .gitignore + requirements.txt
2. Flask app factory (`app/__init__.py`)
3. Config classes (Dev/Prod) with python-dotenv
4. SQLAlchemy models (User, Manual, ManualIndex, ReadingProgress)
5. Alembic setup + initial migration
6. Makefile with `dev`, `test`, `lint`, `db` targets

### Phase 2: Auth & Core Upload (Days 3-4)
1. Auth blueprint (login/logout) + Flask-Login setup
2. `flask create-admin` CLI command
3. Manuals blueprint scaffolding
4. Upload form (Flask-WTF) + validation
5. PDF utils (text extraction with pypdf, SHA256 hash)
6. File storage + duplicate detection
7. FTS5 indexing helper

### Phase 3: Views & Search (Days 5-6)
1. Base template (nav, flash messages, footer)
2. Manuals list (paginated, sortable)
3. Manual detail page (metadata display)
4. PDF.js viewer integration
5. Search blueprint + FTS5 query logic
6. Search results page with filters

### Phase 4: Mobile UX & Progress (Day 7)
1. Reading progress tracking (AJAX endpoint)
2. Mobile-optimized PDF.js viewer:
   - Single-page scroll mode
   - Touch gesture support (pinch-zoom, swipe)
   - Large prev/next buttons (44px min)
   - Page progress indicator
3. Mobile CSS refinements:
   - Card-based list layout (not tables)
   - Bottom navigation or hamburger menu
   - Touch-friendly forms (large inputs, spacing)
   - System font stack for performance
4. Flash messages/toasts (mobile-friendly positioning)
5. Responsive breakpoints (mobile-first: 320px → 768px → 1024px)

### Phase 5: Security & Polish (Days 8-9)
1. Security headers middleware
2. CSRF verification on all forms
3. Structured logging (JSON)
4. Error pages (404, 500)
5. Input sanitization review
6. Tests (upload, search, auth flows)

### Phase 6: Deploy Prep (Day 10)
1. Docker + docker-compose (dev + prod)
2. Gunicorn + Nginx config
3. .env.example documentation
4. README with setup instructions
5. CI/CD pipeline (GitHub Actions)

---

## Mobile UX Requirements (Checklist)

- ✅ **Viewport meta tag** with proper scaling limits
- ✅ **Base font size** ≥16px (prevents iOS zoom on input focus)
- ✅ **Line height** ≥1.5 for readability
- ✅ **Tap targets** ≥44x44px (WCAG AAA standard)
- ✅ **Touch spacing** ≥8px between interactive elements
- ✅ **High contrast** text (4.5:1 minimum for body text)
- ✅ **System fonts** for fast rendering (no web font delays)
- ✅ **Card layout** on mobile (not tables)
- ✅ **PDF viewer** supports pinch-zoom and single-page scroll
- ✅ **Large buttons** for page navigation (prev/next)
- ✅ **Bottom or hamburger nav** for easy thumb access
- ✅ **Loading indicators** for slow network (PDF download)
- ✅ **Landscape mode** tested and functional
- ✅ **Tested on real devices**: iPhone, Android phone, iPad

---

## Definition of Done

- ✅ All MVP features implemented
- ✅ **Mobile UX checklist** 100% complete
- ✅ **Tested on 3+ real mobile devices** (iOS + Android)
- ✅ Tests pass (`pytest` with >80% coverage)
- ✅ Lint passes (`ruff check --fix`)
- ✅ Security headers verified
- ✅ README + .env.example complete
- ✅ Docker build succeeds
- ✅ Can create admin, upload PDF, search, view, track progress **on mobile**

---

*End of CLAUDE.md*
