#!/usr/bin/env python3
"""
Script to create database with session-based schedule
"""
import os
from app import create_app, db
from app.models.user import User
from app.models.class_model import Class
from app.models.student import Student
from app.models.schedule import Schedule
from app.models.attendance import Attendance
from app.models.event import Event
from app.models.finance import Finance
from app.models.time_slot import TimeSlot
from datetime import datetime, time, date

def create_database():
    """Create database and sample data"""
    app = create_app()
    
    with app.app_context():
        # Remove existing database
        if os.path.exists('app.db'):
            os.remove('app.db')
        
        # Create all tables
        db.create_all()

        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='Quản trị viên',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Create manager user if not exists
        manager = User.query.filter_by(username='manager1').first()
        if not manager:
            manager = User(
                username='manager1',
                email='manager1@example.com',
                full_name='Nguyễn Văn Quản',
                role='manager',
                is_active=True
            )
            manager.set_password('manager123')
            db.session.add(manager)

        # Create teacher users if not exist
        teacher1 = User.query.filter_by(username='teacher1').first()
        if not teacher1:
            teacher1 = User(
                username='teacher1',
                email='teacher1@example.com',
                full_name='Trần Thị Lan',
                role='teacher',
                is_active=True
            )
            teacher1.set_password('teacher123')
            db.session.add(teacher1)

        teacher2 = User.query.filter_by(username='teacher2').first()
        if not teacher2:
            teacher2 = User(
                username='teacher2',
                email='teacher2@example.com',
                full_name='Lê Văn Nam',
                role='teacher',
                is_active=True
            )
            teacher2.set_password('teacher123')
            db.session.add(teacher2)
        
        db.session.commit()
        
        # Create classes
        class1 = Class(
            name='10A1',
            description='Lớp 10A1 - Chuyên Toán',
            manager_id=manager.id,
            is_active=True
        )
        db.session.add(class1)

        class2 = Class(
            name='11B2',
            description='Lớp 11B2 - Chuyên Lý',
            manager_id=manager.id,
            is_active=True
        )
        db.session.add(class2)
        
        db.session.commit()
        
        # Create students
        students_data = [
            ('Nguyễn Văn An', 'SV001', '2005-01-15', class1.id),
            ('Trần Thị Bình', 'SV002', '2005-02-20', class1.id),
            ('Lê Văn Cường', 'SV003', '2005-03-10', class1.id),
            ('Phạm Thị Dung', 'SV004', '2004-12-05', class2.id),
            ('Hoàng Văn Em', 'SV005', '2004-11-25', class2.id),
        ]

        for name, student_code, birth_date, class_id in students_data:
            existing_student = Student.query.filter_by(student_code=student_code).first()
            if not existing_student:
                student = Student(
                    full_name=name,
                    student_code=student_code,
                    date_of_birth=datetime.strptime(birth_date, '%Y-%m-%d').date(),
                    class_id=class_id,
                    is_active=True
                )
                db.session.add(student)
        
        db.session.commit()
        
        # Create schedules with session-based system
        schedules_data = [
            # Monday
            (1, 'morning', class1.id, teacher1.id, time(7, 30), time(11, 30), 'Toán', 'A101'),
            (1, 'afternoon', class2.id, teacher2.id, time(13, 30), time(17, 30), 'Lý', 'B201'),
            
            # Tuesday
            (2, 'morning', class2.id, teacher1.id, time(7, 30), time(11, 30), 'Toán', 'A102'),
            (2, 'afternoon', class1.id, teacher2.id, time(13, 30), time(17, 30), 'Hóa', 'B202'),
            
            # Wednesday
            (3, 'morning', class1.id, teacher1.id, time(7, 30), time(11, 30), 'Toán', 'A101'),
            (3, 'afternoon', class2.id, teacher2.id, time(13, 30), time(17, 30), 'Lý', 'B201'),
            
            # Thursday
            (4, 'morning', class2.id, teacher1.id, time(7, 30), time(11, 30), 'Toán', 'A102'),
            (4, 'afternoon', class1.id, teacher2.id, time(13, 30), time(17, 30), 'Hóa', 'B202'),
            
            # Friday
            (5, 'morning', class1.id, teacher1.id, time(7, 30), time(11, 30), 'Toán', 'A101'),
            (5, 'afternoon', class2.id, teacher2.id, time(13, 30), time(17, 30), 'Lý', 'B201'),
        ]
        
        for day, session, class_id, teacher_id, start, end, subject, room in schedules_data:
            schedule = Schedule(
                class_id=class_id,
                teacher_id=teacher_id,
                day_of_week=day,
                session=session,
                start_time=start,
                end_time=end,
                subject=subject,
                room=room,
                is_active=True
            )
            db.session.add(schedule)
        
        db.session.commit()

        # Enroll students in schedules
        from app.models.student_schedule import StudentSchedule

        # Get all students and schedules
        all_students = Student.query.all()
        all_schedules = Schedule.query.all()

        # Enroll students in schedules based on their class
        for student in all_students:
            # Find schedules for this student's class
            class_schedules = [s for s in all_schedules if s.class_id == student.class_id]

            for schedule in class_schedules:
                # Check if already enrolled
                existing = StudentSchedule.query.filter_by(
                    student_id=student.id,
                    schedule_id=schedule.id,
                    is_active=True
                ).first()

                if not existing:
                    enrollment = StudentSchedule(
                        student_id=student.id,
                        schedule_id=schedule.id,
                        is_active=True
                    )
                    db.session.add(enrollment)

        db.session.commit()
        print("Student enrollments created successfully!")

        # Create sample events
        events_data = [
            ('Họp phụ huynh', 'Họp phụ huynh đầu năm học', datetime(2024, 9, 15, 8, 0), datetime(2024, 9, 15, 10, 0), 'Hội trường'),
            ('Thi giữa kỳ', 'Kỳ thi giữa học kỳ I', datetime(2024, 10, 20, 7, 30), datetime(2024, 10, 20, 11, 30), 'Các phòng thi'),
            ('Văn nghệ', 'Chương trình văn nghệ 20/11', datetime(2024, 11, 20, 18, 0), datetime(2024, 11, 20, 21, 0), 'Sân trường'),
        ]

        for name, desc, start_dt, end_dt, location in events_data:
            existing_event = Event.query.filter_by(name=name).first()
            if not existing_event:
                event = Event(
                    name=name,
                    description=desc,
                    start_datetime=start_dt,
                    end_datetime=end_dt,
                    location=location,
                    creator_id=admin.id,
                    is_active=True
                )
                db.session.add(event)
        
        db.session.commit()

        # Assign teachers to classes
        class1.teachers.append(teacher1)
        class1.teachers.append(teacher2)
        class2.teachers.append(teacher1)
        class2.teachers.append(teacher2)

        db.session.commit()

        # Create default time slots
        default_slots = TimeSlot.get_default_slots()
        for slot_data in default_slots:
            existing_slot = TimeSlot.query.filter_by(
                name=slot_data['name'],
                session_type=slot_data['session_type']
            ).first()

            if not existing_slot:
                time_slot = TimeSlot(
                    name=slot_data['name'],
                    session_type=slot_data['session_type'],
                    start_time=datetime.strptime(slot_data['start_time'], '%H:%M').time(),
                    end_time=datetime.strptime(slot_data['end_time'], '%H:%M').time(),
                    description=slot_data['description'],
                    created_by=admin.id
                )
                db.session.add(time_slot)

        db.session.commit()

        print("✅ Database created successfully!")
        print("👤 Admin: admin / admin123")
        print("👤 Manager: manager1 / manager123")
        print("👤 Teacher: teacher1 / teacher123")
        print("👤 Teacher: teacher2 / teacher123")
        print("📚 Classes and teachers assigned successfully!")
        print("⏰ Default time slots created!")

if __name__ == '__main__':
    create_database()
