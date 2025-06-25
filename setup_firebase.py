#!/usr/bin/env python3
"""
Firebase setup script for Vietnamese Classroom Management System
"""

import os
import json
from app import create_app
from app.firebase_config import init_firebase
from app.services.firebase_service import sync_with_firebase

def setup_firebase():
    """Setup Firebase for the application"""
    print("🔥 Firebase Setup for Vietnamese Classroom Management System")
    print("=" * 60)
    
    # Check for Firebase credentials
    firebase_creds = os.environ.get('FIREBASE_CREDENTIALS')
    service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH', 'firebase-service-account.json')
    
    if not firebase_creds and not os.path.exists(service_account_path):
        print("❌ Firebase credentials not found!")
        print("\nPlease set up Firebase credentials:")
        print("1. Option 1: Set FIREBASE_CREDENTIALS environment variable with JSON credentials")
        print("2. Option 2: Place firebase-service-account.json file in project root")
        print("3. Option 3: Set FIREBASE_SERVICE_ACCOUNT_PATH environment variable")
        return False
    
    try:
        # Create app context
        app = create_app()
        
        with app.app_context():
            # Initialize Firebase
            db = init_firebase(app)
            if not db:
                print("❌ Failed to initialize Firebase")
                return False
            
            # Sync data with Firebase
            print("\n🔄 Syncing data with Firebase...")
            success = sync_with_firebase()
            
            if success:
                print("\n✅ Firebase setup completed successfully!")
                print("\n📋 Next steps:")
                print("1. Set USE_FIREBASE=true environment variable")
                print("2. Deploy your application")
                print("3. Your app will now use Firebase as the database")
                return True
            else:
                print("❌ Firebase sync failed")
                return False
                
    except Exception as e:
        print(f"❌ Firebase setup error: {e}")
        return False

def create_sample_firebase_config():
    """Create sample Firebase configuration"""
    sample_config = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project-id.iam.gserviceaccount.com"
    }
    
    with open('firebase-service-account-sample.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print("📄 Created firebase-service-account-sample.json")
    print("Please replace with your actual Firebase service account credentials")

def migrate_to_firebase():
    """Migrate existing SQLAlchemy data to Firebase"""
    print("🔄 Migrating existing data to Firebase...")
    
    try:
        app = create_app()
        
        with app.app_context():
            # Set Firebase flag temporarily
            os.environ['USE_FIREBASE'] = 'false'  # Use SQLAlchemy for reading
            
            from app.models.user import User
            from app.services.firebase_service import UserService
            
            # Initialize Firebase
            init_firebase(app)
            
            # Migrate users
            users = User.query.all()
            migrated_count = 0
            
            for user in users:
                try:
                    UserService.create_user(
                        username=user.username,
                        email=user.email,
                        full_name=user.full_name,
                        role=user.role,
                        password='temp123',  # Users will need to reset passwords
                        phone=user.phone
                    )
                    migrated_count += 1
                except Exception as e:
                    print(f"⚠️  Failed to migrate user {user.username}: {e}")
            
            print(f"✅ Migrated {migrated_count} users to Firebase")
            
            # TODO: Add migration for other models (classes, students, etc.)
            
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'setup':
            setup_firebase()
        elif command == 'migrate':
            migrate_to_firebase()
        elif command == 'sample-config':
            create_sample_firebase_config()
        else:
            print("Usage: python setup_firebase.py [setup|migrate|sample-config]")
    else:
        print("🔥 Firebase Setup Options:")
        print("1. python setup_firebase.py setup - Setup Firebase")
        print("2. python setup_firebase.py migrate - Migrate existing data")
        print("3. python setup_firebase.py sample-config - Create sample config")

if __name__ == "__main__":
    main()
