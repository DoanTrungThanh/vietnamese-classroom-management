# 🔥 Firebase Setup Guide

## Vietnamese Classroom Management System - Firebase Integration

### 📋 Overview

This guide helps you migrate from PostgreSQL to Firebase Firestore for the Vietnamese Classroom Management System.

### 🚀 Quick Setup

#### Step 1: Create Firebase Project

1. **Go to**: [Firebase Console](https://console.firebase.google.com/)
2. **Create** new project: `vietnamese-classroom-management`
3. **Enable** Firestore Database
4. **Generate** service account key:
   - Project Settings → Service Accounts
   - Generate new private key
   - Download JSON file

#### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.firebase.example .env

# Edit .env file with your Firebase credentials
nano .env
```

#### Step 3: Install Dependencies

```bash
pip install firebase-admin google-cloud-firestore
```

#### Step 4: Setup Firebase

```bash
# Setup Firebase (creates default users)
python setup_firebase.py setup

# OR migrate existing data
python setup_firebase.py migrate
```

#### Step 5: Deploy with Firebase

```bash
# Set environment variable
export USE_FIREBASE=true

# Run application
python run.py
```

### 🔧 Configuration Options

#### Option 1: Environment Variable (Recommended for Production)

```bash
export USE_FIREBASE=true
export FIREBASE_CREDENTIALS='{"type":"service_account",...}'
```

#### Option 2: Service Account File (Local Development)

```bash
export USE_FIREBASE=true
export FIREBASE_SERVICE_ACCOUNT_PATH=firebase-service-account.json
```

### 📊 Firebase Collections Structure

```
vietnamese-classroom-management/
├── users/
│   ├── {user_id}
│   │   ├── username: string
│   │   ├── email: string
│   │   ├── full_name: string
│   │   ├── role: string
│   │   └── created_at: timestamp
├── classes/
│   ├── {class_id}
│   │   ├── name: string
│   │   ├── manager_id: string
│   │   └── is_active: boolean
├── students/
│   ├── {student_id}
│   │   ├── full_name: string
│   │   ├── student_code: string
│   │   └── class_id: string
├── schedules/
├── attendance/
├── finance/
├── donations/
└── events/
```

### 🔄 Migration Process

#### Automatic Migration

```bash
python setup_firebase.py migrate
```

#### Manual Migration

1. **Export** existing PostgreSQL data
2. **Transform** to Firebase format
3. **Import** to Firestore collections
4. **Verify** data integrity
5. **Switch** to Firebase mode

### 🛡️ Security Rules

Add these Firestore security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users collection
    match /users/{userId} {
      allow read, write: if request.auth != null;
    }
    
    // Classes collection
    match /classes/{classId} {
      allow read, write: if request.auth != null;
    }
    
    // Students collection
    match /students/{studentId} {
      allow read, write: if request.auth != null;
    }
    
    // Other collections
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

### 🎯 Benefits of Firebase

- ✅ **Real-time updates**
- ✅ **Automatic scaling**
- ✅ **No server maintenance**
- ✅ **Built-in security**
- ✅ **Global CDN**
- ✅ **Offline support**

### 🔧 Troubleshooting

#### Common Issues

1. **Authentication Error**
   ```
   Solution: Check Firebase credentials format
   ```

2. **Permission Denied**
   ```
   Solution: Update Firestore security rules
   ```

3. **Collection Not Found**
   ```
   Solution: Run setup_firebase.py to initialize
   ```

### 📱 Render.com Deployment

#### Environment Variables

```bash
USE_FIREBASE=true
FIREBASE_CREDENTIALS={"type":"service_account",...}
```

#### Build Command

```bash
pip install -r requirements.txt
```

#### Start Command

```bash
python run.py
```

### 🎉 Success Verification

After setup, verify:

1. **Login**: admin/admin123
2. **Create**: New user via admin panel
3. **Check**: Firebase console for new documents
4. **Test**: All CRUD operations

### 📞 Support

If you encounter issues:

1. **Check** Firebase console logs
2. **Verify** environment variables
3. **Test** with sample data
4. **Review** security rules

---

**🔥 Your Vietnamese Classroom Management System is now powered by Firebase!**
