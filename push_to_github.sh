#!/bin/bash
# GitHub Upload Script for Vietnamese Classroom Management System

echo "🚀 Uploading to GitHub..."

# Check if remote origin exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "✅ Remote origin already exists"
else
    echo "❌ Please add remote origin first:"
    echo "   git remote add origin https://github.com/DoanTrungThanh/vietnamese-classroom-management.git"
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
