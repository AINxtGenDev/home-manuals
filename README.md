# House Manuals

A **mobile-first** Flask web application for managing and reading household PDF manuals. Upload, organize, search, and view your appliance and device manuals from any device—optimized for phones and tablets.

## Features

- **Mobile-First Design**: Large tap targets (44px+), readable fonts (16px+ base), touch gestures
- **PDF Upload & Storage**: Secure file handling, duplicate detection via SHA256 hashing
- **Full-Text Search**: SQLite FTS5 search with brand/room/device type filters
- **PDF Viewer**: PDF.js integration with pinch-zoom, page navigation, reading progress tracking
- **Organized Library**: Filter and sort by brand, room, device type, upload date
- **Secure**: Flask-Login authentication, CSRF protection, security headers, input validation

## Quick Start

### Prerequisites

- Python 3.11+
- pip & virtualenv

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/home-manuals.git
cd home-manuals

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install
# or: pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and set a strong SECRET_KEY

# Initialize database
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('✓ Database initialized!')"

# Create admin user
export FLASK_APP=app
flask create-admin
# Enter email and password when prompted
```

### Run Development Server

```bash
make dev
# or: flask run --debug
```

Visit http://localhost:5000 and log in with your admin credentials.

## Usage

### Upload a Manual

1. Click **Upload** in the navigation
2. Select a PDF file (max 50MB)
3. Fill in metadata:
   - **Title** (required): e.g., "Refrigerator User Manual"
   - **Brand** (optional): e.g., "Samsung"
   - **Model** (optional): e.g., "RF28R7351SG"
   - **Device Type** (optional): e.g., "Appliance", "Electronics"
   - **Room/Location** (optional): e.g., "Kitchen"
   - **Year** (optional): e.g., 2023
   - **Tags** (optional): Comma-separated, e.g., "warranty, installation"
4. Click **Upload Manual**

### View & Read Manuals

- Browse all manuals from **Home**
- Use filters to narrow by brand, room, or device type
- Click **View Manual** to open the mobile-optimized PDF viewer
- Navigate pages with large **Prev/Next** buttons
- Pinch-to-zoom on touch devices
- Your reading progress is automatically saved

### Search

- Click **Search** in navigation
- Enter keywords (searches full PDF text)
- Apply optional filters (brand, room, device type)
- Results ranked by relevance

## Development

### Commands

```bash
make dev        # Run development server
make test       # Run tests with coverage
make lint       # Run ruff linter
make format     # Format code with ruff
make db         # Run database migrations (if using Alembic)
make clean      # Clean cache files
```

### Project Structure

```
/home-manuals
  /app                    # Application code
    __init__.py           # Flask app factory
    /blueprints           # Route blueprints (auth, manuals, search)
    models.py             # SQLAlchemy models
    forms.py              # Flask-WTF forms
    pdf_utils.py          # PDF processing
    search_utils.py       # FTS5 search
    security.py           # Security headers
    config.py             # Configuration
    cli.py                # CLI commands
  /templates              # Jinja2 templates
  /static                 # CSS, JS, vendor files
  /instance               # SQLite database (gitignored)
  /storage                # Uploaded PDFs (gitignored)
  /tests                  # Test suite
  /migrations             # Alembic migrations
```

### Mobile UX Checklist

✅ Viewport meta tag with proper scaling
✅ Base font ≥16px
✅ Line height ≥1.5
✅ Tap targets ≥44x44px
✅ Touch spacing ≥8px
✅ High contrast text (4.5:1)
✅ System fonts for fast rendering
✅ Card layout on mobile (not tables)
✅ PDF viewer supports pinch-zoom
✅ Large page navigation buttons
✅ Reading progress tracking

## Security

- **Authentication**: Flask-Login with Werkzeug password hashing (scrypt)
- **CSRF Protection**: Flask-WTF CSRF tokens on all forms
- **File Validation**: Extension whitelist (.pdf), MIME check, PDF magic bytes verification
- **Security Headers**: CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, HSTS (prod)
- **File Storage**: UUID-based naming, SHA256 duplicate detection
- **Secrets**: Stored in `.env` (never committed)

## Configuration

Edit `.env` to customize:

```bash
# Flask
SECRET_KEY=<generate-random-secret-key>
FLASK_ENV=development

# Database (leave empty for default)
DATABASE_URL=

# File Upload
STORAGE_DIR=storage
MAX_FILE_SIZE_MB=50

# Security (set to True in production)
SESSION_COOKIE_SECURE=False
ENABLE_HSTS=False
```

## Testing

```bash
# Run tests with coverage
make test

# Run specific test
pytest tests/test_upload.py -v
```

## Production Deployment

1. Set `FLASK_ENV=production` in `.env`
2. Generate a strong `SECRET_KEY`
3. Set `SESSION_COOKIE_SECURE=True` and `ENABLE_HSTS=True`
4. Use a production WSGI server (Gunicorn included):
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
   ```
5. Set up Nginx reverse proxy
6. Consider Docker deployment (Dockerfile included)

## CLI Commands

```bash
# Create admin user
flask create-admin

# Initialize database
flask init-db

# Rebuild search index
flask reindex
```

## License

MIT License - see [LICENSE](LICENSE)

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Support

For issues, please use the [GitHub issue tracker](https://github.com/yourusername/home-manuals/issues).
