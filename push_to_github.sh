#!/bin/bash
# Script to push code to GitHub with authentication

echo "🚀 Pushing Vietnamese Classroom Management to GitHub..."

# Prompt for GitHub credentials
read -p "Enter your GitHub username: " GITHUB_USERNAME
read -p "Enter your GitHub Personal Access Token: " GITHUB_TOKEN

# Update remote URL with credentials
git remote set-url origin https://$GITHUB_USERNAME:$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/vietnamese-classroom-management.git

echo "📤 Pushing code to GitHub..."

# Push to GitHub
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
    echo "🌐 Repository URL: https://github.com/$GITHUB_USERNAME/vietnamese-classroom-management"
    echo ""
    echo "📋 Next steps:"
    echo "1. Go to https://render.com"
    echo "2. Sign up with GitHub account"
    echo "3. Create new Web Service"
    echo "4. Connect repository: vietnamese-classroom-management"
    echo ""
    echo "🎉 Ready for Render deployment!"
else
    echo "❌ Failed to push to GitHub"
    echo "Please check your credentials and try again"
fi

# Clean up credentials from remote URL for security
git remote set-url origin https://github.com/$GITHUB_USERNAME/vietnamese-classroom-management.git
