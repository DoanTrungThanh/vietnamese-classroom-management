from datetime import datetime, time
from app import db

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 1=Monday, 7=Sunday
    session = db.Column(db.String(20), nullable=False)  # 'morning' or 'afternoon'
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    subject = db.Column(db.String(100))
    room = db.Column(db.String(50))
    week_number = db.Column(db.String(10), nullable=False)  # Format: 2025-W25 - Specific week for this schedule
    week_created = db.Column(db.String(10))  # Week when schedule was created: 2025-W25
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attendances = db.relationship('Attendance', backref='schedule', lazy='dynamic')

    @staticmethod
    def get_current_week():
        """Get current week in YYYY-WXX format"""
        from datetime import datetime
        now = datetime.now()
        year, week, _ = now.isocalendar()
        return f"{year}-W{week:02d}"

    @staticmethod
    def get_next_week():
        """Get next week in YYYY-WXX format"""
        from datetime import datetime, timedelta
        next_week_date = datetime.now() + timedelta(weeks=1)
        year, week, _ = next_week_date.isocalendar()
        return f"{year}-W{week:02d}"

    @staticmethod
    def get_week_from_date(date_obj):
        """Get week string from date object"""
        year, week, _ = date_obj.isocalendar()
        return f"{year}-W{week:02d}"

    def __repr__(self):
        return f'<Schedule {self.class_obj.name if self.class_obj else "Unknown"} - Day {self.day_of_week} Session {self.session} Week {self.week_number}>'
    
    @property
    def day_name(self):
        days = {
            1: 'Thứ 2',
            2: 'Thứ 3', 
            3: 'Thứ 4',
            4: 'Thứ 5',
            5: 'Thứ 6',
            6: 'Thứ 7',
            7: 'Chủ nhật'
        }
        return days.get(self.day_of_week, '')
    
    @property
    def time_range(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

    @property
    def session_name(self):
        return 'Buổi sáng' if self.session == 'morning' else 'Buổi chiều'

    def get_color(self):
        """Get color for calendar display"""
        if self.session == 'morning':
            return '#007bff'  # Blue
        elif self.session == 'afternoon':
            return '#28a745'  # Green
        else:
            return '#ffc107'  # Yellow for evening

    @staticmethod
    def get_current_week():
        """Get current week in format YYYY-WXX"""
        from datetime import datetime
        now = datetime.now()
        year, week, _ = now.isocalendar()
        return f"{year}-W{week:02d}"

    @staticmethod
    def get_next_week():
        """Get next week in format YYYY-WXX"""
        from datetime import datetime, timedelta
        next_week = datetime.now() + timedelta(weeks=1)
        year, week, _ = next_week.isocalendar()
        return f"{year}-W{week:02d}"

    def confirm_for_week(self, week_number=None):
        """Confirm schedule for specific week - TODO: Implement after migration"""
        # if not week_number:
        #     week_number = self.get_current_week()
        # self.week_number = week_number
        # self.is_confirmed = True
        pass

    @staticmethod
    def get_week_from_date(date_obj):
        """Get week number from date object"""
        year, week, _ = date_obj.isocalendar()
        return f"{year}-W{week:02d}"
