from datetime import datetime
from app import db

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # present, absent_with_reason, absent_without_reason
    reason = db.Column(db.Text)  # Lý do nghỉ học nếu vắng
    check_in_time = db.Column(db.DateTime)  # Thời gian vào lớp
    check_out_time = db.Column(db.DateTime)  # Thời gian ra lớp
    lesson_content = db.Column(db.Text)  # Nội dung bài giảng
    notes = db.Column(db.Text)  # Ghi chú
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Attendance {self.student.full_name} - {self.date} - {self.status}>'
    
    @property
    def status_display(self):
        status_map = {
            'present': 'Có mặt',
            'absent_with_reason': 'Vắng có lý do',
            'absent_without_reason': 'Vắng không lý do'
        }
        return status_map.get(self.status, self.status)
