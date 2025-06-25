"""
Firebase configuration and initialization
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import current_app

# Global Firestore client
db = None

def init_firebase(app=None):
    """Initialize Firebase with app context"""
    global db
    
    try:
        # Get Firebase credentials from environment variable
        firebase_creds = os.environ.get('FIREBASE_CREDENTIALS')
        
        if firebase_creds:
            # Parse JSON credentials from environment variable
            cred_dict = json.loads(firebase_creds)
            cred = credentials.Certificate(cred_dict)
        else:
            # Fallback to service account file (for local development)
            service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH', 'firebase-service-account.json')
            if os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
            else:
                # Use default credentials (for Google Cloud deployment)
                cred = credentials.ApplicationDefault()
        
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        # Initialize Firestore client
        db = firestore.client()
        
        if app:
            app.logger.info("✅ Firebase Firestore initialized successfully")
        else:
            print("✅ Firebase Firestore initialized successfully")
            
        return db
        
    except Exception as e:
        error_msg = f"❌ Firebase initialization failed: {str(e)}"
        if app:
            app.logger.error(error_msg)
        else:
            print(error_msg)
        return None

def get_firestore_client():
    """Get Firestore client instance"""
    global db
    if db is None:
        db = init_firebase()
    return db

class FirestoreModel:
    """Base class for Firestore models"""
    
    collection_name = None
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.id = kwargs.get('id')
    
    @classmethod
    def get_collection(cls):
        """Get Firestore collection reference"""
        db = get_firestore_client()
        if db and cls.collection_name:
            return db.collection(cls.collection_name)
        return None
    
    @classmethod
    def create(cls, data):
        """Create new document"""
        try:
            collection = cls.get_collection()
            if collection:
                doc_ref = collection.add(data)
                return doc_ref[1].id  # Return document ID
        except Exception as e:
            print(f"Error creating document: {e}")
        return None
    
    @classmethod
    def get_by_id(cls, doc_id):
        """Get document by ID"""
        try:
            collection = cls.get_collection()
            if collection:
                doc = collection.document(doc_id).get()
                if doc.exists:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    return cls(**data)
        except Exception as e:
            print(f"Error getting document: {e}")
        return None
    
    @classmethod
    def get_all(cls, limit=None, order_by=None):
        """Get all documents"""
        try:
            collection = cls.get_collection()
            if collection:
                query = collection
                if order_by:
                    query = query.order_by(order_by)
                if limit:
                    query = query.limit(limit)
                
                docs = query.stream()
                results = []
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    results.append(cls(**data))
                return results
        except Exception as e:
            print(f"Error getting documents: {e}")
        return []
    
    @classmethod
    def query(cls, field, operator, value):
        """Query documents"""
        try:
            collection = cls.get_collection()
            if collection:
                docs = collection.where(field, operator, value).stream()
                results = []
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    results.append(cls(**data))
                return results
        except Exception as e:
            print(f"Error querying documents: {e}")
        return []
    
    def save(self):
        """Save document"""
        try:
            collection = self.get_collection()
            if collection:
                data = self.to_dict()
                if self.id:
                    # Update existing document
                    collection.document(self.id).set(data)
                else:
                    # Create new document
                    doc_ref = collection.add(data)
                    self.id = doc_ref[1].id
                return True
        except Exception as e:
            print(f"Error saving document: {e}")
        return False
    
    def delete(self):
        """Delete document"""
        try:
            if self.id:
                collection = self.get_collection()
                if collection:
                    collection.document(self.id).delete()
                    return True
        except Exception as e:
            print(f"Error deleting document: {e}")
        return False
    
    def to_dict(self):
        """Convert model to dictionary"""
        data = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_') and key != 'id':
                data[key] = value
        return data

def migrate_to_firebase():
    """Migrate existing SQLAlchemy data to Firebase"""
    try:
        from app.models.user import User
        from app.models.class_model import Class
        from app.models.student import Student
        # Import other models as needed
        
        print("🔄 Starting migration to Firebase...")
        
        # Migrate users
        users = User.query.all()
        for user in users:
            user_data = {
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone,
                'role': user.role,
                'is_active': user.is_active,
                'password_hash': user.password_hash,
                'created_at': user.created_at
            }
            FirebaseUser.create(user_data)
        
        print(f"✅ Migrated {len(users)} users")
        
        # Add migration for other models...
        
        print("🎉 Migration to Firebase completed!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

# Firebase model classes
class FirebaseUser(FirestoreModel):
    collection_name = 'users'

class FirebaseClass(FirestoreModel):
    collection_name = 'classes'

class FirebaseStudent(FirestoreModel):
    collection_name = 'students'

class FirebaseSchedule(FirestoreModel):
    collection_name = 'schedules'

class FirebaseAttendance(FirestoreModel):
    collection_name = 'attendance'

class FirebaseFinance(FirestoreModel):
    collection_name = 'finance'

class FirebaseDonation(FirestoreModel):
    collection_name = 'donations'

class FirebaseEvent(FirestoreModel):
    collection_name = 'events'
