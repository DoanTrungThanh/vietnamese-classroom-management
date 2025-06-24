#!/usr/bin/env python3
"""
Script to reset database and create fresh data
"""

import os
from datetime import datetime, date, time
from app import create_app, db
from app.models.user import User
from app.models.class_model import Class
from app.models.student import Student
from app.models.schedule import Schedule
from app.models.time_slot import TimeSlot

def reset_database():
    app = create_app()
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        
        print("Database reset successfully!")
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@school.edu.vn',
            full_name='Quản trị viên',
            phone='0123456789',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create manager users
        manager1 = User(
            username='manager1',
            email='manager1@school.edu.vn',
            full_name='Nguyễn Văn Quản',
            phone='0987654321',
            role='manager'
        )
        manager1.set_password('manager123')
        db.session.add(manager1)
        
        # Create teacher users
        teacher1 = User(
            username='teacher1',
            email='teacher1@school.edu.vn',
            full_name='Lê Văn Giáo',
            phone='0912345678',
            role='teacher'
        )
        teacher1.set_password('teacher123')
        db.session.add(teacher1)
        
        teacher2 = User(
            username='teacher2',
            email='teacher2@school.edu.vn',
            full_name='Phạm Thị Viên',
            phone='0912345679',
            role='teacher'
        )
        teacher2.set_password('teacher123')
        db.session.add(teacher2)

        # Create user with limited permissions
        user1 = User(
            username='user1',
            email='user1@school.edu.vn',
            full_name='Nguyễn Văn User',
            phone='0912345681',
            role='user'
        )
        user1.set_password('user123')
        db.session.add(user1)

        db.session.commit()
        
        # Create time slots with evening sessions
        time_slots = [
            # Morning sessions
            TimeSlot(name='Tiết 1', start_time=time(7, 30), end_time=time(8, 15), session_type='morning'),
            TimeSlot(name='Tiết 2', start_time=time(8, 15), end_time=time(9, 0), session_type='morning'),
            TimeSlot(name='Tiết 3', start_time=time(9, 15), end_time=time(10, 0), session_type='morning'),
            TimeSlot(name='Tiết 4', start_time=time(10, 0), end_time=time(10, 45), session_type='morning'),
            TimeSlot(name='Tiết 5', start_time=time(10, 45), end_time=time(11, 30), session_type='morning'),

            # Afternoon sessions
            TimeSlot(name='Tiết 6', start_time=time(13, 30), end_time=time(14, 15), session_type='afternoon'),
            TimeSlot(name='Tiết 7', start_time=time(14, 15), end_time=time(15, 0), session_type='afternoon'),
            TimeSlot(name='Tiết 8', start_time=time(15, 15), end_time=time(16, 0), session_type='afternoon'),
            TimeSlot(name='Tiết 9', start_time=time(16, 0), end_time=time(16, 45), session_type='afternoon'),
            TimeSlot(name='Tiết 10', start_time=time(16, 45), end_time=time(17, 30), session_type='afternoon'),

            # Evening sessions
            TimeSlot(name='Tiết 11', start_time=time(18, 0), end_time=time(18, 45), session_type='evening'),
            TimeSlot(name='Tiết 12', start_time=time(18, 45), end_time=time(19, 30), session_type='evening'),
            TimeSlot(name='Tiết 13', start_time=time(19, 30), end_time=time(20, 15), session_type='evening'),
            TimeSlot(name='Tiết 14', start_time=time(20, 15), end_time=time(21, 0), session_type='evening'),
        ]
        
        for slot in time_slots:
            db.session.add(slot)
        
        db.session.commit()
        
        print("Fresh database created successfully!")
        print("\nLogin credentials:")
        print("Admin: admin / admin123")
        print("Manager: manager1 / manager123")
        print("Teacher 1: teacher1 / teacher123")
        print("Teacher 2: teacher2 / teacher123")
        print("User: user1 / user123")
        print("\nTime slots created with morning, afternoon, and evening sessions!")

if __name__ == '__main__':
    reset_database()
