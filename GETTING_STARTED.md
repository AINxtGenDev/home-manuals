# Getting Started with House Manuals

## 🚀 Quick Start (5 minutes)

Your House Manuals app is **ready to run**! The database is initialized and an admin user has been created.

### Default Admin Credentials

```
Email: admin@example.com
Password: admin123
```

⚠️ **Important**: Change these credentials after first login!

### Start the Application

```bash
# Make sure you're in the project directory
cd /home/wpl/02_development/04_house_manuals/home-manuals

# Activate the virtual environment (if using venv)
source home-manuals/bin/activate  # or: source venv/bin/activate

# Start the development server
make dev
# or: flask run --debug
```

The app will be available at: **http://localhost:5000**

## 📱 Mobile Testing

This app is designed **mobile-first**. To test on your phone:

1. Find your computer's local IP:
   ```bash
   ip addr show | grep "inet 192"  # Linux/WSL
   # or: ipconfig | findstr IPv4     # Windows
   ```

2. Run Flask with host binding:
   ```bash
   flask run --debug --host=0.0.0.0 --port=5000
   ```

3. On your phone, visit: `http://YOUR_IP:5000`

## 📋 First Steps

1. **Login** at http://localhost:5000/auth/login
   - Use the default credentials above

2. **Upload your first manual**:
   - Click "Upload" in the navigation
   - Select a PDF file
   - Fill in the title (required) and any optional metadata
   - Click "Upload Manual"

3. **View your manual**:
   - Click "Home" to see all manuals
   - Click "View Manual" on any card
   - Test the mobile PDF viewer:
     - Use Prev/Next buttons to navigate
     - Pinch-to-zoom (on touch devices)
     - Your reading progress is auto-saved

4. **Try searching**:
   - Click "Search"
   - Enter keywords (searches full PDF text)
   - Apply filters by brand, room, or device type

## 🔐 Change Admin Password

After first login, create a new admin user:

```bash
export FLASK_APP=app
flask create-admin
# Enter a NEW email and strong password
```

Then log in with the new account and optionally delete the default admin.

## 📁 Project Structure

```
home-manuals/
├── app/                  # Application code
│   ├── blueprints/       # Routes (auth, manuals, search)
│   ├── models.py         # Database models
│   ├── forms.py          # WTForms
│   └── templates/        # HTML templates
├── static/               # CSS, JS
├── instance/             # SQLite database (gitignored)
├── storage/              # Uploaded PDFs (gitignored)
├── .env                  # Environment variables (gitignored)
└── README.md             # Full documentation
```

## ⚙️ Configuration

Edit `.env` to customize:

- `SECRET_KEY`: Generate a new one for production!
- `MAX_FILE_SIZE_MB`: Default is 50MB
- `STORAGE_DIR`: Where PDFs are stored (default: ./storage)

## 🧪 Testing Features

Try these features:

- ✅ Upload a manual with metadata (brand, model, room, tags)
- ✅ Filter manuals by brand, room, or device type
- ✅ Sort manuals by title, brand, or upload date
- ✅ Search for keywords in PDF content
- ✅ View a PDF and navigate pages
- ✅ Zoom in/out on the PDF viewer
- ✅ Check reading progress persistence (reload page, it remembers your page)
- ✅ Upload a duplicate PDF (should detect and warn)

## 🐛 Troubleshooting

### Port 5000 already in use

```bash
flask run --port=5001
```

### Database errors

Reinitialize the database:

```bash
rm instance/home_manuals.db
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
flask create-admin
```

### Import errors

Make sure dependencies are installed:

```bash
pip install -r requirements.txt
```

## 📚 Next Steps

- Read the full [README.md](README.md) for deployment instructions
- Check [CLAUDE.md](CLAUDE.md) for the complete project specification
- Start uploading your household manuals!

## 🎯 Pro Tips

1. **Organize by rooms**: Use the "Room" field to group manuals by location
2. **Tag warranty info**: Add "warranty" tags to manuals you need to keep track of
3. **Searchable PDFs work best**: Scanned PDFs without OCR won't be searchable
4. **Mobile reading**: The app remembers which page you're on, perfect for reading manuals on the go

---

**Enjoy your House Manuals app!** 📖✨
