"""
Firebase service layer for database operations
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.firebase_config import (
    FirebaseUser, FirebaseClass, FirebaseStudent, 
    FirebaseSchedule, FirebaseAttendance, FirebaseFinance,
    FirebaseDonation, FirebaseEvent
)

class UserService:
    """User management with Firebase"""
    
    @staticmethod
    def create_user(username, email, full_name, role, password, phone=None):
        """Create new user"""
        user_data = {
            'username': username,
            'email': email,
            'full_name': full_name,
            'phone': phone,
            'role': role,
            'is_active': True,
            'password_hash': generate_password_hash(password),
            'created_at': datetime.utcnow()
        }
        return FirebaseUser.create(user_data)
    
    @staticmethod
    def get_user_by_username(username):
        """Get user by username"""
        users = FirebaseUser.query('username', '==', username)
        return users[0] if users else None
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        users = FirebaseUser.query('email', '==', email)
        return users[0] if users else None
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return FirebaseUser.get_by_id(user_id)
    
    @staticmethod
    def get_all_users():
        """Get all users"""
        return FirebaseUser.get_all(order_by='created_at')
    
    @staticmethod
    def verify_password(user, password):
        """Verify user password"""
        return check_password_hash(user.password_hash, password)
    
    @staticmethod
    def update_user(user_id, data):
        """Update user"""
        user = FirebaseUser.get_by_id(user_id)
        if user:
            for key, value in data.items():
                setattr(user, key, value)
            return user.save()
        return False

class ClassService:
    """Class management with Firebase"""
    
    @staticmethod
    def create_class(name, description, manager_id):
        """Create new class"""
        class_data = {
            'name': name,
            'description': description,
            'manager_id': manager_id,
            'is_active': True,
            'created_at': datetime.utcnow()
        }
        return FirebaseClass.create(class_data)
    
    @staticmethod
    def get_all_classes():
        """Get all active classes"""
        return FirebaseClass.query('is_active', '==', True)
    
    @staticmethod
    def get_classes_by_manager(manager_id):
        """Get classes managed by specific manager"""
        return FirebaseClass.query('manager_id', '==', manager_id)

class StudentService:
    """Student management with Firebase"""
    
    @staticmethod
    def create_student(full_name, student_code, date_of_birth=None, phone=None, address=None, class_id=None):
        """Create new student"""
        student_data = {
            'full_name': full_name,
            'student_code': student_code,
            'date_of_birth': date_of_birth,
            'phone': phone,
            'address': address,
            'class_id': class_id,
            'is_active': True,
            'created_at': datetime.utcnow()
        }
        return FirebaseStudent.create(student_data)
    
    @staticmethod
    def get_students_by_class(class_id):
        """Get students in specific class"""
        return FirebaseStudent.query('class_id', '==', class_id)
    
    @staticmethod
    def get_all_students():
        """Get all active students"""
        return FirebaseStudent.query('is_active', '==', True)

class FinanceService:
    """Financial management with Firebase"""
    
    @staticmethod
    def create_transaction(transaction_type, amount, description, category, creator_id, transaction_date=None):
        """Create financial transaction"""
        finance_data = {
            'type': transaction_type,
            'amount': amount,
            'description': description,
            'category': category,
            'creator_id': creator_id,
            'transaction_date': transaction_date or datetime.utcnow().date(),
            'created_at': datetime.utcnow()
        }
        return FirebaseFinance.create(finance_data)
    
    @staticmethod
    def get_transactions_by_date_range(start_date, end_date):
        """Get transactions in date range"""
        # Note: Firestore range queries need composite indexes
        transactions = FirebaseFinance.get_all()
        filtered = []
        for t in transactions:
            if start_date <= t.transaction_date <= end_date:
                filtered.append(t)
        return filtered

class DonationService:
    """Donation management with Firebase"""
    
    @staticmethod
    def create_donation(asset_name, donor_name, quantity, estimated_value, creator_id):
        """Create donation record"""
        donation_data = {
            'asset_name': asset_name,
            'donor_name': donor_name,
            'quantity': quantity,
            'estimated_value': estimated_value,
            'status': 'received',
            'creator_id': creator_id,
            'donation_date': datetime.utcnow().date(),
            'created_at': datetime.utcnow()
        }
        return FirebaseDonation.create(donation_data)
    
    @staticmethod
    def get_donations_by_status(status):
        """Get donations by status"""
        return FirebaseDonation.query('status', '==', status)

def initialize_default_data():
    """Initialize default data in Firebase"""
    try:
        # Check if admin user exists
        admin_user = UserService.get_user_by_username('admin')
        if not admin_user:
            # Create default admin user
            UserService.create_user(
                username='admin',
                email='admin@qllhttbb.vn',
                full_name='Administrator',
                role='admin',
                password='admin123'
            )
            print("✅ Default admin user created")
        
        # Create sample managers
        manager1 = UserService.get_user_by_username('manager1')
        if not manager1:
            UserService.create_user(
                username='manager1',
                email='manager1@qllhttbb.vn',
                full_name='Quản sinh 1',
                role='manager',
                password='manager123'
            )
        
        # Create sample teachers
        teacher1 = UserService.get_user_by_username('teacher1')
        if not teacher1:
            UserService.create_user(
                username='teacher1',
                email='teacher1@qllhttbb.vn',
                full_name='Giáo viên 1',
                role='teacher',
                password='teacher123'
            )
        
        print("✅ Default users initialized in Firebase")
        
    except Exception as e:
        print(f"❌ Error initializing default data: {e}")

def sync_with_firebase():
    """Sync local database with Firebase"""
    try:
        print("🔄 Starting Firebase sync...")
        initialize_default_data()
        print("🎉 Firebase sync completed!")
        return True
    except Exception as e:
        print(f"❌ Firebase sync failed: {e}")
        return False
