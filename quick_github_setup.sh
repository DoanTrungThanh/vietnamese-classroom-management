#!/bin/bash
# Quick GitHub Setup for Vietnamese Classroom Management System

echo "🎓 Vietnamese Classroom Management System - Quick GitHub Setup"
echo "=============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install Git first."
    exit 1
fi

print_status "Git is installed"

# Initialize git repository if not exists
if [ ! -d ".git" ]; then
    print_info "Initializing Git repository..."
    git init
    print_status "Git repository initialized"
else
    print_info "Git repository already exists"
fi

# Configure git user
print_info "Configuring Git user..."
git config user.name "Vietnamese Classroom Management"
git config user.email "admin@qllhttbb.vn"
print_status "Git user configured"

# Create .env.example if not exists
if [ ! -f ".env.example" ]; then
    print_info "Creating .env.example..."
    cat > .env.example << 'EOF'
# Environment variables for production deployment
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=postgresql://username:password@hostname:port/database

# Optional: Flask app configuration
FLASK_APP=run.py
EOF
    print_status "Created .env.example"
fi

# Create run.py if not exists
if [ ! -f "run.py" ]; then
    print_info "Creating run.py..."
    cat > run.py << 'EOF'
#!/usr/bin/env python3
"""
Main application runner for the Vietnamese Classroom Management System
"""

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
    print("\nDefault login credentials:")
    print("Username: admin")
    print("Password: admin123")

    app.run(debug=debug, host='0.0.0.0', port=port)
EOF
    print_status "Created run.py"
fi

# Add all files to git
print_info "Adding files to Git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    print_warning "No changes to commit"
else
    # Commit changes
    print_info "Committing changes..."
    git commit -m "Vietnamese Classroom Management System - $(date '+%Y-%m-%d %H:%M:%S')"
    print_status "Changes committed"
fi

# Create push script
print_info "Creating push script..."
cat > push_to_github.sh << 'EOF'
#!/bin/bash
# Push to GitHub script

echo "🚀 Pushing to GitHub..."

# Check if remote origin exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "✅ Remote origin exists"
    
    # Push to GitHub
    echo "📤 Pushing to main branch..."
    git branch -M main
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully pushed to GitHub!"
        echo "🔗 Repository: $(git remote get-url origin)"
        echo ""
        echo "🚀 Ready for Render deployment!"
        echo "1. Go to https://render.com"
        echo "2. Create Web Service from GitHub"
        echo "3. Build Command: pip install -r requirements.txt"
        echo "4. Start Command: python run.py"
        echo "5. Add environment variables"
        echo "6. Deploy!"
    else
        echo "❌ Failed to push to GitHub"
    fi
else
    echo "❌ No remote origin found!"
    echo "Please add remote origin first:"
    echo "git remote add origin https://github.com/YOUR_USERNAME/vietnamese-classroom-management.git"
fi
EOF

chmod +x push_to_github.sh
print_status "Created push_to_github.sh"

echo ""
echo "🎉 Git setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://github.com/new"
echo "2. Repository name: vietnamese-classroom-management"
echo "3. Description: Vietnamese Classroom Management System"
echo "4. Public repository (recommended)"
echo "5. Don't add README, .gitignore, or license"
echo "6. Create repository"
echo "7. Copy the repository URL"
echo "8. Add remote origin:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/vietnamese-classroom-management.git"
echo "9. Push to GitHub:"
echo "   ./push_to_github.sh"
echo ""
echo "🚀 After GitHub upload, deploy on Render.com:"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: python run.py"
echo ""
print_status "Ready for GitHub upload!"
