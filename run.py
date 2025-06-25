#!/usr/bin/env python3
"""
Main application runner for the classroom management system
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

    # Initialize database and create admin user
    with app.app_context():
        try:
            # Check if using Firebase
            from app import USE_FIREBASE

            if USE_FIREBASE:
                # Initialize Firebase and sync data
                from app.services.firebase_service import sync_with_firebase
                sync_with_firebase()
                print("✅ Firebase initialized and synced!")
            else:
                # Initialize SQLAlchemy database
                db.create_all()
                print("Database initialized successfully!")

                # Create default admin user if not exists
                admin = User.query.filter_by(username='admin').first()
                if not admin:
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
                    print("✅ Admin user created: admin/admin123")
                else:
                    print("✅ Admin user already exists")

        except Exception as e:
            print(f"Database initialization error: {e}")

    print("Starting Vietnamese Classroom Management System...")
    print(f"Server running on port: {port}")
    print("\nDefault login credentials:")
    print("Username: admin")
    print("Password: admin123")

    app.run(debug=debug, host='0.0.0.0', port=port)
