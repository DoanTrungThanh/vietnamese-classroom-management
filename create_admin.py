#!/usr/bin/env python3
"""
Create admin user for Vietnamese Classroom Management System
"""

import os
import sys
from app import create_app, db
from app.models import User

def create_admin_user():
    """Create default admin user"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if admin user already exists
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("✅ Admin user already exists")
                print(f"   Username: admin")
                print(f"   Email: {admin.email}")
                print(f"   Role: {admin.role}")
                print(f"   Active: {admin.is_active}")
                return True
            
            # Create admin user
            admin = User(
                username='admin',
                email='admin@qllhttbb.vn',
                full_name='Administrator',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Admin user created successfully!")
            print("   Username: admin")
            print("   Password: admin123")
            print("   Email: admin@qllhttbb.vn")
            print("   Role: admin")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            db.session.rollback()
            return False

def create_sample_users():
    """Create sample users for testing"""
    app = create_app()
    
    with app.app_context():
        try:
            # Sample users data
            sample_users = [
                {
                    'username': 'manager1',
                    'email': 'manager1@qllhttbb.vn',
                    'full_name': 'Quản sinh 1',
                    'role': 'manager',
                    'password': 'manager123'
                },
                {
                    'username': 'manager2',
                    'email': 'manager2@qllhttbb.vn',
                    'full_name': 'Quản sinh 2',
                    'role': 'manager',
                    'password': 'manager123'
                },
                {
                    'username': 'teacher1',
                    'email': 'teacher1@qllhttbb.vn',
                    'full_name': 'Giáo viên 1',
                    'role': 'teacher',
                    'password': 'teacher123'
                },
                {
                    'username': 'teacher2',
                    'email': 'teacher2@qllhttbb.vn',
                    'full_name': 'Giáo viên 2',
                    'role': 'teacher',
                    'password': 'teacher123'
                },
                {
                    'username': 'teacher3',
                    'email': 'teacher3@qllhttbb.vn',
                    'full_name': 'Giáo viên 3',
                    'role': 'teacher',
                    'password': 'teacher123'
                }
            ]
            
            created_count = 0
            for user_data in sample_users:
                # Check if user already exists
                existing_user = User.query.filter_by(username=user_data['username']).first()
                if not existing_user:
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        full_name=user_data['full_name'],
                        role=user_data['role'],
                        is_active=True
                    )
                    user.set_password(user_data['password'])
                    db.session.add(user)
                    created_count += 1
                    print(f"✅ Created user: {user_data['username']}")
            
            if created_count > 0:
                db.session.commit()
                print(f"✅ Created {created_count} sample users")
            else:
                print("✅ All sample users already exist")
                
            return True
            
        except Exception as e:
            print(f"❌ Error creating sample users: {e}")
            db.session.rollback()
            return False

def main():
    """Main function"""
    print("🎓 Vietnamese Classroom Management System - User Creation")
    print("=" * 60)
    
    # Create admin user
    print("Creating admin user...")
    if not create_admin_user():
        sys.exit(1)
    
    print("\nCreating sample users...")
    if not create_sample_users():
        print("⚠️  Warning: Failed to create sample users")
    
    print("\n🎉 User creation completed!")
    print("\n📋 Login credentials:")
    print("Admin:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nManagers:")
    print("  Username: manager1 | Password: manager123")
    print("  Username: manager2 | Password: manager123")
    print("\nTeachers:")
    print("  Username: teacher1 | Password: teacher123")
    print("  Username: teacher2 | Password: teacher123")
    print("  Username: teacher3 | Password: teacher123")

if __name__ == "__main__":
    main()
