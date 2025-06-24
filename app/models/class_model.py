from datetime import datetime
from app import db

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # Ví dụ: 10A1
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', backref='class_obj', lazy='dynamic')
    schedules = db.relationship('Schedule', backref='class_obj', lazy='dynamic')
    
    # Many-to-many relationship with teachers
    teachers = db.relationship('User', secondary='class_teacher',
                             primaryjoin='Class.id == class_teacher.c.class_id',
                             secondaryjoin='User.id == class_teacher.c.teacher_id',
                             backref='teaching_classes')

    def __repr__(self):
        return f'<Class {self.name} - {self.block_name}>'
    
    @property
    def student_count(self):
        return self.students.filter_by(is_active=True).count()

# Association table for many-to-many relationship between Class and Teacher
class_teacher = db.Table('class_teacher',
    db.Column('class_id', db.Integer, db.ForeignKey('class.id'), primary_key=True),
    db.Column('teacher_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)
