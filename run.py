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
    # Check if database exists, if not create it
    with app.app_context():
        if not os.path.exists('app.db'):
            db.create_all()
            print("Database created successfully!")
        else:
            print("Database already exists.")

    print("Starting Classroom Management System...")
    print("Access the application at: http://127.0.0.1:8000")
    print("\nLogin credentials:")
    print("Admin: admin / admin123")
    print("Manager 1: manager1 / manager123")
    print("Manager 2: manager2 / manager123")
    print("Teacher 1: teacher1 / teacher123")
    print("Teacher 2: teacher2 / teacher123")
    print("Teacher 3: teacher3 / teacher123")
    print("\nPress Ctrl+C to stop the server")

    app.run(debug=True, host='0.0.0.0', port=8000)
