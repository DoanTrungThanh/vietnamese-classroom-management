from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False)  # admin, manager, teacher, user
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    managed_blocks = db.relationship('Class', backref='manager', lazy='dynamic',
                                   foreign_keys='Class.manager_id')
    teaching_schedules = db.relationship('Schedule', backref='teacher', lazy='dynamic')
    created_events = db.relationship('Event', backref='creator', lazy='dynamic')
    finance_records = db.relationship('Finance', backref='creator', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_manager(self):
        return self.role == 'manager'
    
    def is_teacher(self):
        return self.role == 'teacher'

    def is_user(self):
        return self.role == 'user'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
