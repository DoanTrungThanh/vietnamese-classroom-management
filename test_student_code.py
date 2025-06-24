#!/usr/bin/env python3
"""
Test script to verify student code generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.student import Student
import hashlib
from datetime import datetime

def test_generate_student_code():
    """Test the student code generation function"""
    
    def generate_student_code():
        """Generate unique student code using hash starting from 1000"""
        import hashlib
        from datetime import datetime

        # Start from 1000 and find next available number
        base_number = 1000

        while True:
            # Check if this number already exists as student code
            student_code = str(base_number)
            existing = Student.query.filter_by(student_code=student_code).first()

            if not existing:
                # Found available number, optionally add hash for extra uniqueness
                timestamp = str(datetime.now().timestamp())
                hash_input = f"{base_number}{timestamp}"
                hash_object = hashlib.md5(hash_input.encode())
                hash_suffix = hash_object.hexdigest()[:2].upper()

                # For simplicity, just return the base number
                # You can uncomment below line to add hash suffix: 1000AB, 1001CD, etc.
                # student_code = f"{base_number}{hash_suffix}"

                return student_code

            # If exists, try next number
            base_number += 1

            # Safety check to prevent infinite loop
            if base_number > 9999:
                # Fallback to timestamp-based code if we run out of 4-digit numbers
                timestamp = str(int(datetime.now().timestamp()))[-4:]
                return f"HS{timestamp}"
    
    app = create_app()
    
    with app.app_context():
        print("Testing student code generation...")
        
        # Get current student count
        current_count = Student.query.count()
        print(f"Current student count: {current_count}")
        
        # Generate 10 test codes
        print("\nGenerating 10 test student codes:")
        for i in range(10):
            code = generate_student_code()
            print(f"  {i+1}. {code}")
            
            # Simulate adding a student to increment count
            # (We won't actually add to DB, just increment our counter)
            current_count += 1
        
        print(f"\nNext expected code would start from: {1000 + Student.query.count()}")

if __name__ == "__main__":
    test_generate_student_code()
