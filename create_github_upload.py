#!/usr/bin/env python3
"""
Create zip file for manual GitHub upload
"""
import os
import zipfile
import shutil
from datetime import datetime

def create_github_upload():
    """Create clean zip file for GitHub upload"""
    
    print("📦 Creating GitHub upload package...")
    
    # Create clean directory
    upload_dir = "github_upload"
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    os.makedirs(upload_dir)
    
    # Files and directories to include
    include_items = [
        'app/',
        'migrations/',
        'app.py',
        'config.py',
        'requirements_render.txt',
        'build.sh',
        '.env.render',
        'RENDER_STEP_BY_STEP.md',
        'DEPLOY_NOW.md',
        'QUICK_RENDER_GUIDE.md'
    ]
    
    # Copy files
    for item in include_items:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.copytree(item, os.path.join(upload_dir, item))
                print(f"✅ Copied directory: {item}")
            else:
                shutil.copy2(item, upload_dir)
                print(f"✅ Copied file: {item}")
        else:
            print(f"⚠️  Not found: {item}")
    
    # Create README.md for GitHub
    readme_content = """# Vietnamese Classroom Management System

A comprehensive web application for managing Vietnamese language classes, students, schedules, and finances.

## Features

- **User Management**: Admin, Manager, and Teacher roles with different permissions
- **Class Management**: Create and manage classes with student enrollment
- **Student Management**: Add students with auto-generated codes
- **Schedule Management**: Weekly schedule creation with copy functionality
- **Attendance Tracking**: Mark attendance for each session
- **Financial Management**: Track income, expenses, and donations
- **Notification System**: Generate parent communication templates
- **Export Functions**: Excel export capabilities

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **Deployment**: Render.com

## Quick Deploy to Render.com

1. **Fork/Clone** this repository
2. **Go to** [Render.com](https://render.com)
3. **Create Web Service** from GitHub repository
4. **Configure**:
   - Build Command: `./build.sh`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`
5. **Add Environment Variables**:
   ```
   SECRET_KEY=your-secret-key
   FLASK_ENV=production
   FLASK_DEBUG=False
   DATABASE_URL=postgresql://...
   ```
6. **Create PostgreSQL database** and connect

## Default Login

- **Username**: `admin`
- **Password**: `admin123`

## Documentation

- [Detailed Deployment Guide](RENDER_STEP_BY_STEP.md)
- [Quick Deploy Guide](DEPLOY_NOW.md)

## License

MIT License
"""
    
    with open(os.path.join(upload_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✅ Created README.md")
    
    # Create .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Flask
instance/
.webassets-cache

# Environment variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Deployment
static_export/
*.zip
"""
    
    with open(os.path.join(upload_dir, '.gitignore'), 'w') as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore")
    
    # Create zip file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"vietnamese-classroom-management-{timestamp}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(upload_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, upload_dir)
                zipf.write(file_path, arcname)
    
    print(f"📦 Created zip file: {zip_filename}")
    
    # Cleanup
    shutil.rmtree(upload_dir)
    
    print("\n📋 Manual GitHub Upload Instructions:")
    print("1. Go to https://github.com/new")
    print("2. Create repository: vietnamese-classroom-management")
    print("3. Don't add README, .gitignore, or license")
    print("4. After creating, click 'uploading an existing file'")
    print(f"5. Upload the zip file: {zip_filename}")
    print("6. GitHub will extract it automatically")
    print("7. Commit the files")
    print("\n🎉 Ready for Render deployment!")
    
    return zip_filename

if __name__ == "__main__":
    create_github_upload()
