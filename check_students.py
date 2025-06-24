#!/usr/bin/env python3
"""
Check current students in database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.student import Student

def check_students():
    """Check current students in database"""
    
    app = create_app()
    
    with app.app_context():
        print("Current students in database:")
        students = Student.query.all()
        
        print(f"Total students: {len(students)}")
        print("\nStudent codes:")
        for student in students:
            print(f"  ID: {student.id}, Code: {student.student_code}, Name: {student.full_name}, Active: {student.is_active}")

if __name__ == "__main__":
    check_students()
