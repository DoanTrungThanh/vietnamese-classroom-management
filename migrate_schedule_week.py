#!/usr/bin/env python3
"""
Migration script to add week tracking columns to Schedule table
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add week tracking columns to Schedule table"""
    
    db_path = 'classroom_management.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(schedule)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add week_created column if not exists
        if 'week_created' not in columns:
            print("Adding week_created column...")
            cursor.execute("ALTER TABLE schedule ADD COLUMN week_created VARCHAR(10)")
            
        # Add week_number column if not exists
        if 'week_number' not in columns:
            print("Adding week_number column...")
            cursor.execute("ALTER TABLE schedule ADD COLUMN week_number VARCHAR(10)")
            
        # Add is_confirmed column if not exists
        if 'is_confirmed' not in columns:
            print("Adding is_confirmed column...")
            cursor.execute("ALTER TABLE schedule ADD COLUMN is_confirmed BOOLEAN DEFAULT 0")
        
        # Update existing schedules with current week data
        print("Updating existing schedules...")
        
        # Get current week
        now = datetime.now()
        year, week, _ = now.isocalendar()
        current_week = f"{year}-W{week:02d}"
        
        # Update all existing schedules
        cursor.execute("""
            UPDATE schedule 
            SET week_created = ?, 
                week_number = ?, 
                is_confirmed = 1 
            WHERE week_created IS NULL OR week_number IS NULL
        """, (current_week, current_week))
        
        conn.commit()
        print(f"Migration completed successfully! Updated {cursor.rowcount} schedules.")
        
        # Show updated table structure
        cursor.execute("PRAGMA table_info(schedule)")
        columns = cursor.fetchall()
        print("\nUpdated Schedule table structure:")
        for column in columns:
            print(f"  {column[1]} {column[2]} {'NOT NULL' if column[3] else ''} {'DEFAULT ' + str(column[4]) if column[4] else ''}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("Starting Schedule table migration...")
    success = migrate_database()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
