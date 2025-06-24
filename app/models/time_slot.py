from app import db
from datetime import datetime

class TimeSlot(db.Model):
    """Model for time slots/periods"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # Ví dụ: "Tiết 1", "Buổi sáng"
    session_type = db.Column(db.String(20), nullable=False)  # morning, afternoon, evening
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    creator = db.relationship('User', backref='created_time_slots')
    
    def __repr__(self):
        return f'<TimeSlot {self.name}: {self.start_time}-{self.end_time}>'
    
    @property
    def time_range(self):
        """Get formatted time range"""
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
    
    @property
    def session_name(self):
        """Get Vietnamese session name"""
        session_names = {
            'morning': 'Buổi sáng',
            'afternoon': 'Buổi chiều', 
            'evening': 'Buổi tối'
        }
        return session_names.get(self.session_type, self.session_type)
    
    def get_color(self):
        """Get color for display"""
        colors = {
            'morning': '#ff6b35',
            'afternoon': '#ff8c42',
            'evening': '#ffa726'
        }
        return colors.get(self.session_type, '#6c757d')
    
    @classmethod
    def get_by_session(cls, session_type):
        """Get all time slots for a session type"""
        return cls.query.filter_by(session_type=session_type, is_active=True).order_by(cls.start_time).all()
    
    @classmethod
    def get_default_slots(cls):
        """Get default time slots if none exist"""
        return [
            {
                'name': 'Buổi sáng',
                'session_type': 'morning',
                'start_time': '07:30',
                'end_time': '11:30',
                'description': 'Khung giờ học buổi sáng'
            },
            {
                'name': 'Buổi chiều',
                'session_type': 'afternoon', 
                'start_time': '13:30',
                'end_time': '17:30',
                'description': 'Khung giờ học buổi chiều'
            },
            {
                'name': 'Buổi tối',
                'session_type': 'evening',
                'start_time': '18:00',
                'end_time': '21:00',
                'description': 'Khung giờ học buổi tối'
            }
        ]
