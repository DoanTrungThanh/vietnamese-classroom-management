#!/bin/bash
# Setup GitHub repository for Render deployment

echo "🚀 Setting up GitHub repository for Vietnamese Classroom Management..."

# Prompt for GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

# Update remote URL
git remote set-url origin https://github.com/$GITHUB_USERNAME/vietnamese-classroom-management.git

echo "✅ Updated remote URL to: https://github.com/$GITHUB_USERNAME/vietnamese-classroom-management.git"

# Push to GitHub
echo "📤 Pushing code to GitHub..."
git push -u origin main

echo "✅ Code pushed to GitHub successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://render.com"
echo "2. Sign up with your GitHub account"
echo "3. Create new Web Service"
echo "4. Connect your repository: vietnamese-classroom-management"
echo ""
echo "🎉 Ready for Render deployment!"
