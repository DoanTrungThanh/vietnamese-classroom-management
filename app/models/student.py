from datetime import datetime
from app import db

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_code = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.Text)
    parent_name = db.Column(db.String(100))
    parent_phone = db.Column(db.String(20))
    profile_url = db.Column(db.String(500))  # URL to Google Drive or internal system
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attendances = db.relationship('Attendance', backref='student', lazy='dynamic')
    event_participations = db.relationship('EventParticipant', backref='student', lazy='dynamic')

    def __repr__(self):
        return f'<Student {self.student_code} - {self.full_name}>'
    
    @property
    def attendance_rate(self):
        """Calculate attendance rate for this student"""
        total_sessions = self.attendances.count()
        if total_sessions == 0:
            return 0
        present_sessions = self.attendances.filter_by(status='present').count()
        return round((present_sessions / total_sessions) * 100, 2)
