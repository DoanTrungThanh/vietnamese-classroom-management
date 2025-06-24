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
