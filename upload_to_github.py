#!/usr/bin/env python3
"""
Upload Vietnamese Classroom Management System to GitHub
"""
import os
import subprocess
import sys
from datetime import datetime

def run_command(command, description=""):
    """Run shell command and handle errors"""
    print(f"🔄 {description}")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Error: {description}")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def setup_git_repository():
    """Setup git repository and upload to GitHub"""
    
    print("🚀 Setting up Git repository for Vietnamese Classroom Management System")
    print("=" * 70)
    
    # Check if git is installed
    if not run_command("git --version", "Checking Git installation"):
        print("❌ Git is not installed. Please install Git first.")
        return False
    
    # Initialize git repository
    if not os.path.exists('.git'):
        if not run_command("git init", "Initializing Git repository"):
            return False
    
    # Configure git user (if not already configured)
    run_command("git config user.name 'Vietnamese Classroom Management'", "Setting Git username")
    run_command("git config user.email 'admin@qllhttbb.vn'", "Setting Git email")
    
    # Create .gitignore if not exists
    gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
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
MANIFEST

# Flask stuff
instance/
.webassets-cache

# Environment variables
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.env.local
.env.production

# Database files
*.db
*.sqlite
*.sqlite3
app.db
app.db.backup

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Deployment files
*.zip
*.tar.gz

# Temporary files
temp/
tmp/
"""
    
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("✅ Created .gitignore")
    
    # Create run.py if missing
    if not os.path.exists('run.py'):
        run_py_content = """#!/usr/bin/env python3
\"\"\"
Main application runner for the Vietnamese Classroom Management System
\"\"\"

import os
from app import create_app, db
from app.models import User, Class, Student, Schedule, Attendance, Event, Finance

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Class': Class, 
        'Student': Student,
        'Schedule': Schedule, 
        'Attendance': Attendance, 
        'Event': Event, 
        'Finance': Finance
    }

if __name__ == '__main__':
    # Production configuration for Render
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Initialize database
    with app.app_context():
        try:
            db.create_all()
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Database initialization: {e}")

    print("Starting Vietnamese Classroom Management System...")
    print(f"Server running on port: {port}")
    print("\\nDefault login credentials:")
    print("Username: admin")
    print("Password: admin123")

    app.run(debug=debug, host='0.0.0.0', port=port)
"""
        with open('run.py', 'w') as f:
            f.write(run_py_content)
        print("✅ Created run.py")
    
    # Add all files
    if not run_command("git add .", "Adding all files to Git"):
        return False
    
    # Check if there are changes to commit
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        print("ℹ️  No changes to commit")
        return True
    
    # Commit changes
    commit_message = f"Vietnamese Classroom Management System - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        return False
    
    print("\n🎯 Git repository setup completed!")
    print("\n📋 Next steps to upload to GitHub:")
    print("1. Go to https://github.com/new")
    print("2. Repository name: vietnamese-classroom-management")
    print("3. Description: Vietnamese Classroom Management System")
    print("4. Public repository (recommended for Render)")
    print("5. Don't add README, .gitignore, or license")
    print("6. Create repository")
    print("7. Copy the repository URL")
    print("8. Run the following commands:")
    print(f"   git remote add origin https://github.com/YOUR_USERNAME/vietnamese-classroom-management.git")
    print(f"   git branch -M main")
    print(f"   git push -u origin main")
    
    return True

def create_github_commands():
    """Create script with GitHub upload commands"""
    
    script_content = """#!/bin/bash
# GitHub Upload Script for Vietnamese Classroom Management System

echo "🚀 Uploading to GitHub..."

# Check if remote origin exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "✅ Remote origin already exists"
else
    echo "❌ Please add remote origin first:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/vietnamese-classroom-management.git"
    exit 1
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully uploaded to GitHub!"
    echo "🔗 Repository URL: $(git remote get-url origin)"
    echo ""
    echo "🚀 Ready for Render deployment:"
    echo "1. Go to https://render.com"
    echo "2. Create Web Service from GitHub repository"
    echo "3. Build Command: pip install -r requirements.txt"
    echo "4. Start Command: python run.py"
    echo "5. Add environment variables"
    echo "6. Deploy!"
else
    echo "❌ Failed to upload to GitHub"
    echo "Please check your repository URL and permissions"
fi
"""
    
    with open('push_to_github.sh', 'w') as f:
        f.write(script_content)
    
    # Make script executable
    os.chmod('push_to_github.sh', 0o755)
    print("✅ Created push_to_github.sh script")

def main():
    """Main function"""
    print("🎓 Vietnamese Classroom Management System - GitHub Upload Setup")
    print("=" * 70)
    
    # Setup git repository
    if setup_git_repository():
        create_github_commands()
        
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Summary:")
        print("✅ Git repository initialized")
        print("✅ Files added and committed")
        print("✅ Upload script created")
        
        print("\n🚀 Next steps:")
        print("1. Create GitHub repository at https://github.com/new")
        print("2. Add remote origin:")
        print("   git remote add origin https://github.com/YOUR_USERNAME/vietnamese-classroom-management.git")
        print("3. Run upload script:")
        print("   ./push_to_github.sh")
        
        print("\n🎯 After GitHub upload:")
        print("1. Go to Render.com")
        print("2. Create Web Service from your GitHub repository")
        print("3. Use these settings:")
        print("   - Build Command: pip install -r requirements.txt")
        print("   - Start Command: python run.py")
        print("4. Add environment variables from .env.example")
        print("5. Deploy and enjoy!")
        
    else:
        print("❌ Setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
