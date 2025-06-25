"""
Firebase authentication adapter for Flask-Login
"""

from flask_login import UserMixin
from app.services.firebase_service import UserService

class FirebaseUser(UserMixin):
    """Firebase User class compatible with Flask-Login"""
    
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.full_name = user_data.get('full_name')
        self.phone = user_data.get('phone')
        self.role = user_data.get('role')
        self.is_active = user_data.get('is_active', True)
        self.password_hash = user_data.get('password_hash')
        self.created_at = user_data.get('created_at')
    
    def get_id(self):
        """Return user ID for Flask-Login"""
        return str(self.id)
    
    def is_authenticated(self):
        """Return True if user is authenticated"""
        return True
    
    def is_anonymous(self):
        """Return True if user is anonymous"""
        return False
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def is_manager(self):
        """Check if user is manager"""
        return self.role == 'manager'
    
    def is_teacher(self):
        """Check if user is teacher"""
        return self.role == 'teacher'
    
    def check_password(self, password):
        """Check password"""
        return UserService.verify_password(self, password)
    
    def set_password(self, password):
        """Set password"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    @staticmethod
    def get(user_id):
        """Get user by ID for Flask-Login user_loader"""
        firebase_user = UserService.get_user_by_id(user_id)
        if firebase_user:
            return FirebaseUser(firebase_user.to_dict())
        return None
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        firebase_user = UserService.get_user_by_username(username)
        if firebase_user:
            user_data = firebase_user.to_dict()
            user_data['id'] = firebase_user.id
            return FirebaseUser(user_data)
        return None
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        firebase_user = UserService.get_user_by_email(email)
        if firebase_user:
            user_data = firebase_user.to_dict()
            user_data['id'] = firebase_user.id
            return FirebaseUser(user_data)
        return None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at
        }

def load_user(user_id):
    """User loader function for Flask-Login"""
    return FirebaseUser.get(user_id)
