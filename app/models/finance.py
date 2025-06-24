from datetime import datetime
from app import db

class Finance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # income, expense
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))  # Loại khoản mục
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))  # Optional: gán cho lớp
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))  # Optional: gán cho sự kiện
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    related_class = db.relationship('Class', backref='finance_records')
    related_event = db.relationship('Event', backref='finance_records')

    def __repr__(self):
        return f'<Finance {self.type} - {self.amount}>'
    
    @property
    def type_display(self):
        return 'Thu' if self.type == 'income' else 'Chi'
    
    @property
    def formatted_amount(self):
        return f"{self.amount:,.0f} VNĐ"
