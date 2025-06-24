#!/usr/bin/env python3
"""
Script to create sample data for the classroom management system
"""

from datetime import datetime, date, time
from app import create_app, db
from app.models.user import User
from app.models.class_model import Class
from app.models.student import Student
from app.models.schedule import Schedule

def create_sample_data():
    app = create_app()
    with app.app_context():
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
        
        manager2 = User(
            username='manager2',
            email='manager2@school.edu.vn',
            full_name='Trần Thị Sinh',
            phone='0987654322',
            role='manager'
        )
        manager2.set_password('manager123')
        db.session.add(manager2)
        
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
        
        teacher3 = User(
            username='teacher3',
            email='teacher3@school.edu.vn',
            full_name='Hoàng Văn Dạy',
            phone='0912345680',
            role='teacher'
        )
        teacher3.set_password('teacher123')
        db.session.add(teacher3)
        
        db.session.commit()
        
        # Create classes
        class1 = Class(
            name='10A1',
            block_name='Khối 10',
            description='Lớp 10A1 - Chuyên Toán',
            manager_id=manager1.id
        )
        db.session.add(class1)
        
        class2 = Class(
            name='10A2',
            block_name='Khối 10',
            description='Lớp 10A2 - Chuyên Lý',
            manager_id=manager1.id
        )
        db.session.add(class2)
        
        class3 = Class(
            name='11B1',
            block_name='Khối 11',
            description='Lớp 11B1 - Chuyên Hóa',
            manager_id=manager2.id
        )
        db.session.add(class3)
        
        db.session.commit()
        
        # Add teachers to classes
        class1.teachers.append(teacher1)
        class1.teachers.append(teacher2)
        class2.teachers.append(teacher2)
        class2.teachers.append(teacher3)
        class3.teachers.append(teacher1)
        class3.teachers.append(teacher3)
        
        # Create students
        students_data = [
            # Class 10A1
            ('HS001', 'Nguyễn Văn An', date(2008, 1, 15), 'Hà Nội', 'Nguyễn Văn Bình', '0901234567'),
            ('HS002', 'Trần Thị Bảo', date(2008, 3, 22), 'Hà Nội', 'Trần Văn Cường', '0901234568'),
            ('HS003', 'Lê Văn Cường', date(2008, 5, 10), 'Hà Nội', 'Lê Thị Dung', '0901234569'),
            ('HS004', 'Phạm Thị Dung', date(2008, 7, 8), 'Hà Nội', 'Phạm Văn Em', '0901234570'),
            ('HS005', 'Hoàng Văn Em', date(2008, 9, 12), 'Hà Nội', 'Hoàng Thị Phượng', '0901234571'),
            
            # Class 10A2
            ('HS006', 'Vũ Thị Giang', date(2008, 2, 20), 'Hà Nội', 'Vũ Văn Hải', '0901234572'),
            ('HS007', 'Đỗ Văn Hùng', date(2008, 4, 18), 'Hà Nội', 'Đỗ Thị Lan', '0901234573'),
            ('HS008', 'Bùi Thị Linh', date(2008, 6, 25), 'Hà Nội', 'Bùi Văn Minh', '0901234574'),
            ('HS009', 'Ngô Văn Nam', date(2008, 8, 30), 'Hà Nội', 'Ngô Thị Oanh', '0901234575'),
            ('HS010', 'Đinh Thị Phương', date(2008, 10, 5), 'Hà Nội', 'Đinh Văn Quang', '0901234576'),
            
            # Class 11B1
            ('HS011', 'Lý Văn Sơn', date(2007, 1, 12), 'Hà Nội', 'Lý Thị Tâm', '0901234577'),
            ('HS012', 'Cao Thị Uyên', date(2007, 3, 28), 'Hà Nội', 'Cao Văn Vinh', '0901234578'),
            ('HS013', 'Phan Văn Xuân', date(2007, 5, 16), 'Hà Nội', 'Phan Thị Yến', '0901234579'),
            ('HS014', 'Tạ Thị Zung', date(2007, 7, 22), 'Hà Nội', 'Tạ Văn An', '0901234580'),
            ('HS015', 'Mai Văn Bình', date(2007, 9, 8), 'Hà Nội', 'Mai Thị Cúc', '0901234581'),
        ]
        
        class_assignments = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3]
        
        for i, (code, name, dob, address, parent, phone) in enumerate(students_data):
            student = Student(
                student_code=code,
                full_name=name,
                date_of_birth=dob,
                address=address,
                parent_name=parent,
                parent_phone=phone,
                class_id=class_assignments[i]
            )
            db.session.add(student)
        
        # Create sample schedules
        schedules_data = [
            # Monday
            (1, 1, 1, 1, time(7, 30), time(8, 15), 'Toán', 'A101'),
            (1, 2, 2, 1, time(7, 30), time(8, 15), 'Lý', 'B201'),
            (1, 3, 3, 2, time(8, 30), time(9, 15), 'Hóa', 'C301'),
            
            # Tuesday
            (2, 1, 2, 2, time(7, 30), time(8, 15), 'Văn', 'A102'),
            (2, 2, 1, 3, time(8, 30), time(9, 15), 'Toán', 'A101'),
            (2, 3, 3, 1, time(9, 30), time(10, 15), 'Hóa', 'C301'),
            
            # Wednesday
            (3, 1, 1, 1, time(7, 30), time(8, 15), 'Toán', 'A101'),
            (3, 2, 3, 2, time(8, 30), time(9, 15), 'Anh', 'B202'),
            (3, 3, 2, 3, time(9, 30), time(10, 15), 'Lý', 'B201'),
            
            # Thursday
            (4, 1, 2, 2, time(7, 30), time(8, 15), 'Văn', 'A102'),
            (4, 2, 1, 1, time(8, 30), time(9, 15), 'Toán', 'A101'),
            (4, 3, 3, 3, time(9, 30), time(10, 15), 'Hóa', 'C301'),
            
            # Friday
            (5, 1, 3, 3, time(7, 30), time(8, 15), 'Anh', 'B202'),
            (5, 2, 2, 2, time(8, 30), time(9, 15), 'Lý', 'B201'),
            (5, 3, 1, 1, time(9, 30), time(10, 15), 'Toán', 'A101'),
        ]
        
        for day, period, class_id, teacher_id, start, end, subject, room in schedules_data:
            schedule = Schedule(
                class_id=class_id,
                teacher_id=teacher_id,
                day_of_week=day,
                period=period,
                start_time=start,
                end_time=end,
                subject=subject,
                room=room
            )
            db.session.add(schedule)
        
        db.session.commit()
        print("Sample data created successfully!")
        print("\nLogin credentials:")
        print("Admin: admin / admin123")
        print("Manager 1: manager1 / manager123")
        print("Manager 2: manager2 / manager123")
        print("Teacher 1: teacher1 / teacher123")
        print("Teacher 2: teacher2 / teacher123")
        print("Teacher 3: teacher3 / teacher123")

if __name__ == '__main__':
    create_sample_data()
