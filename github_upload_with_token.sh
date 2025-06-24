#!/bin/bash
# GitHub Upload Script with Token Support
# Vietnamese Classroom Management System

echo "🚀 GitHub Upload with Authentication Support"
echo "============================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# Check if GitHub CLI is available
if command -v gh &> /dev/null; then
    print_info "GitHub CLI detected. Using gh for authentication."
    
    # Check if authenticated
    if gh auth status &> /dev/null; then
        print_status "Already authenticated with GitHub CLI"
        
        # Create and push repository
        print_info "Creating repository and pushing..."
        gh repo create vietnamese-classroom-management --public --source=. --remote=origin --push
        
        if [ $? -eq 0 ]; then
            print_status "Successfully uploaded to GitHub with GitHub CLI!"
            REPO_URL="https://github.com/$(gh api user --jq .login)/vietnamese-classroom-management"
            echo -e "${BLUE}🔗 Repository: $REPO_URL${NC}"
            
            echo ""
            print_status "Ready for Render deployment!"
            echo "1. Go to https://render.com"
            echo "2. Create Web Service from GitHub repository"
            echo "3. Repository URL: $REPO_URL"
            echo "4. Build Command: pip install -r requirements.txt"
            echo "5. Start Command: python run.py"
            echo "6. Add environment variables"
            echo "7. Deploy!"
            exit 0
        else
            print_error "Failed to upload with GitHub CLI"
            exit 1
        fi
    else
        print_warning "Not authenticated with GitHub CLI"
        echo "Please run: gh auth login"
        echo "Then run this script again"
        exit 1
    fi
else
    print_warning "GitHub CLI not found"
    echo ""
    print_info "Manual setup required with Personal Access Token"
    echo ""
    echo "📋 Step-by-step instructions:"
    echo ""
    echo "1️⃣  Create Personal Access Token:"
    echo "   • Go to: https://github.com/settings/tokens"
    echo "   • Click 'Generate new token (classic)'"
    echo "   • Note: 'Vietnamese Classroom Management'"
    echo "   • Scopes: ✅ repo, ✅ workflow"
    echo "   • Generate and copy the token"
    echo ""
    echo "2️⃣  Setup remote with token:"
    echo "   git remote remove origin 2>/dev/null || true"
    echo "   git remote add origin https://YOUR_TOKEN@github.com/DoanTrungThanh/vietnamese-classroom-management.git"
    echo ""
    echo "3️⃣  Push to GitHub:"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
    echo "🚀 Alternative: Install GitHub CLI for easier setup:"
    echo "   macOS: brew install gh"
    echo "   Windows: winget install --id GitHub.cli"
    echo "   Then run: gh auth login"
    echo ""
    
    # Ask if user wants to proceed manually
    read -p "Do you have a Personal Access Token ready? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        print_info "Please enter your Personal Access Token:"
        read -s TOKEN
        
        if [ -z "$TOKEN" ]; then
            print_error "No token provided"
            exit 1
        fi
        
        print_info "Setting up remote with token..."
        git remote remove origin 2>/dev/null || true
        git remote add origin https://$TOKEN@github.com/DoanTrungThanh/vietnamese-classroom-management.git
        
        print_info "Pushing to GitHub..."
        git branch -M main
        git push -u origin main
        
        if [ $? -eq 0 ]; then
            print_status "Successfully uploaded to GitHub!"
            echo -e "${BLUE}🔗 Repository: https://github.com/DoanTrungThanh/vietnamese-classroom-management${NC}"
            
            echo ""
            print_status "Ready for Render deployment!"
            echo "1. Go to https://render.com"
            echo "2. Create Web Service from GitHub repository"
            echo "3. Repository URL: https://github.com/DoanTrungThanh/vietnamese-classroom-management"
            echo "4. Build Command: pip install -r requirements.txt"
            echo "5. Start Command: python run.py"
            echo "6. Add environment variables"
            echo "7. Deploy!"
        else
            print_error "Failed to push to GitHub"
            echo "Please check your token and repository permissions"
        fi
    else
        print_info "Please create a Personal Access Token first, then run this script again"
    fi
fi
