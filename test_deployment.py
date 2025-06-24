#!/usr/bin/env python3
"""
Test deployment readiness for Render.com
"""
import os
import subprocess
import sys

def test_deployment_readiness():
    """Test if project is ready for Render deployment"""
    
    print("🔍 Testing deployment readiness for Render.com...")
    
    tests_passed = 0
    total_tests = 8
    
    # Test 1: Check requirements_render.txt
    if os.path.exists('requirements_render.txt'):
        print("✅ requirements_render.txt exists")
        tests_passed += 1
    else:
        print("❌ requirements_render.txt missing")
    
    # Test 2: Check build.sh
    if os.path.exists('build.sh'):
        if os.access('build.sh', os.X_OK):
            print("✅ build.sh exists and is executable")
            tests_passed += 1
        else:
            print("❌ build.sh exists but not executable")
    else:
        print("❌ build.sh missing")
    
    # Test 3: Check app.py
    if os.path.exists('app.py'):
        print("✅ app.py exists")
        tests_passed += 1
    else:
        print("❌ app.py missing")
    
    # Test 4: Check config.py
    if os.path.exists('config.py'):
        with open('config.py', 'r') as f:
            content = f.read()
            if 'postgresql://' in content:
                print("✅ config.py has PostgreSQL support")
                tests_passed += 1
            else:
                print("❌ config.py missing PostgreSQL support")
    else:
        print("❌ config.py missing")
    
    # Test 5: Check health endpoint
    try:
        with open('app/routes/main.py', 'r') as f:
            content = f.read()
            if '/health' in content:
                print("✅ Health endpoint exists")
                tests_passed += 1
            else:
                print("❌ Health endpoint missing")
    except:
        print("❌ Cannot check health endpoint")
    
    # Test 6: Check environment variables template
    if os.path.exists('.env.render'):
        print("✅ .env.render template exists")
        tests_passed += 1
    else:
        print("❌ .env.render template missing")
    
    # Test 7: Check Git repository
    if os.path.exists('.git'):
        print("✅ Git repository initialized")
        tests_passed += 1
    else:
        print("❌ Git repository not initialized")
    
    # Test 8: Test imports
    try:
        sys.path.insert(0, '.')
        from app import create_app
        print("✅ App imports successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Import error: {e}")
    
    # Summary
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Ready for Render deployment")
        print("\n📋 Next steps:")
        print("1. Run: ./setup_github.sh")
        print("2. Go to https://render.com")
        print("3. Follow RENDER_STEP_BY_STEP.md")
        return True
    else:
        print("⚠️  Some tests failed. Please fix issues before deploying.")
        return False

def show_deployment_summary():
    """Show deployment configuration summary"""
    print("\n📋 Deployment Configuration Summary:")
    print("=" * 50)
    
    print("🔧 Build Settings:")
    print("  Build Command: ./build.sh")
    print("  Start Command: gunicorn --bind 0.0.0.0:$PORT app:app")
    print("  Python Version: 3.11")
    
    print("\n🌍 Environment Variables:")
    if os.path.exists('.env.render'):
        with open('.env.render', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key = line.split('=')[0]
                    print(f"  {key}=***")
    
    print("\n🗄️ Database:")
    print("  Type: PostgreSQL")
    print("  Plan: Free (1GB)")
    print("  Region: Singapore")
    
    print("\n🌐 Service:")
    print("  Name: vietnamese-classroom-management")
    print("  Region: Singapore")
    print("  Plan: Free (750 hours/month)")

if __name__ == "__main__":
    if test_deployment_readiness():
        show_deployment_summary()
