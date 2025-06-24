#!/usr/bin/env python3
"""
Database initialization script for manual deployment
Run this via browser after uploading files
"""

import sys
import os
import cgitb

# Enable CGI error reporting
cgitb.enable()

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("Content-Type: text/html\n")
print("<html><head><title>Database Initialization</title></head><body>")
print("<h1>Vietnamese Classroom Management - Database Setup</h1>")

try:
    from app import create_app, db
    from app.models import User, Class, Student, Schedule, TimeSlot
    
    app = create_app()
    
    with app.app_context():
        print("<h2>Creating database tables...</h2>")
        
        # Create all tables
        db.create_all()
        print("<p>✅ Database tables created successfully!</p>")
        
        # Check if admin user already exists
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            print("<p>⚠️ Admin user already exists!</p>")
        else:
            # Create admin user
            admin = User(username='admin', email='admin@qllhttbb.vn', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create sample manager
            manager = User(username='manager', email='manager@qllhttbb.vn', role='manager')
            manager.set_password('manager123')
            db.session.add(manager)
            
            # Create sample teacher
            teacher = User(username='teacher', email='teacher@qllhttbb.vn', role='teacher')
            teacher.set_password('teacher123')
            db.session.add(teacher)
            
            db.session.commit()
            print("<p>✅ Admin user created successfully!</p>")
            print("<p>✅ Sample users created!</p>")
        
        # Create default time slots
        time_slots = [
            TimeSlot(name='Sáng 1', start_time='07:00', end_time='08:30'),
            TimeSlot(name='Sáng 2', start_time='08:45', end_time='10:15'),
            TimeSlot(name='Chiều 1', start_time='14:00', end_time='15:30'),
            TimeSlot(name='Chiều 2', start_time='15:45', end_time='17:15'),
            TimeSlot(name='Tối 1', start_time='18:00', end_time='19:30'),
            TimeSlot(name='Tối 2', start_time='19:45', end_time='21:15'),
        ]
        
        for slot in time_slots:
            existing_slot = TimeSlot.query.filter_by(name=slot.name).first()
            if not existing_slot:
                db.session.add(slot)
        
        db.session.commit()
        print("<p>✅ Default time slots created!</p>")
        
        print("<h2>Setup Complete!</h2>")
        print("<p><strong>Login Credentials:</strong></p>")
        print("<ul>")
        print("<li>Admin: username=<code>admin</code>, password=<code>admin123</code></li>")
        print("<li>Manager: username=<code>manager</code>, password=<code>manager123</code></li>")
        print("<li>Teacher: username=<code>teacher</code>, password=<code>teacher123</code></li>")
        print("</ul>")
        
        print("<p><a href='/' style='background: #f97316; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>Go to Application</a></p>")
        
except Exception as e:
    print(f"<h2>Error occurred:</h2>")
    print(f"<p style='color: red;'>{str(e)}</p>")
    print("<p>Please check:</p>")
    print("<ul>")
    print("<li>Database connection settings in .env file</li>")
    print("<li>Python modules are installed</li>")
    print("<li>File permissions are correct</li>")
    print("</ul>")

print("</body></html>")
