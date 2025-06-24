from datetime import datetime
from app import db

class StudentSchedule(db.Model):
    """Association table for students and schedules (many-to-many)"""
    __tablename__ = 'student_schedule'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    enrolled_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Unique constraint to prevent duplicate enrollments
    __table_args__ = (db.UniqueConstraint('student_id', 'schedule_id', name='unique_student_schedule'),)

    # Relationships
    student = db.relationship('Student', backref='schedule_enrollments')
    schedule = db.relationship('Schedule', backref='student_enrollments')
    
    def __repr__(self):
        return f'<StudentSchedule {self.student.full_name} - {self.schedule.subject}>'
    
    @classmethod
    def enroll_student(cls, student_id, schedule_id):
        """Enroll a student in a schedule"""
        existing = cls.query.filter_by(
            student_id=student_id,
            schedule_id=schedule_id,
            is_active=True
        ).first()
        
        if existing:
            return existing
        
        enrollment = cls(
            student_id=student_id,
            schedule_id=schedule_id,
            is_active=True
        )
        db.session.add(enrollment)
        return enrollment
    
    @classmethod
    def unenroll_student(cls, student_id, schedule_id):
        """Unenroll a student from a schedule"""
        enrollment = cls.query.filter_by(
            student_id=student_id,
            schedule_id=schedule_id,
            is_active=True
        ).first()
        
        if enrollment:
            enrollment.is_active = False
            return enrollment
        return None
