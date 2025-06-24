# ⚡ Quick cPanel Setup - Vietnamese Classroom Management

## 🎯 **Bạn đã có file**: `qllhttbb_deployment_20250624_184304.zip`

---

## 🚀 **5 Bước Deploy (15 phút)**

### **Bước 1: Setup Database (3 phút)**

1. **Login cPanel** → **MySQL Databases**
2. **Create Database**: `qllhttbb_classroom`
3. **Create User**: 
   - Username: `qllhttbb_admin`
   - Password: `ClassRoom2024!`
4. **Add User to Database** → **ALL PRIVILEGES**

### **Bước 2: Upload Files (5 phút)**

1. **cPanel** → **File Manager**
2. **Navigate** to `public_html/`
3. **Upload** `qllhttbb_deployment_20250624_184304.zip`
4. **Right-click** → **Extract**
5. **Delete** zip file sau khi extract

### **Bước 3: Configure Environment (2 phút)**

**Tạo file `.env`** trong `public_html/`:

```bash
SECRET_KEY=QllhTtbb2024SuperSecretKeyForProduction
DATABASE_URL=mysql://qllhttbb_admin:ClassRoom2024!@localhost/qllhttbb_classroom
FLASK_ENV=production
FLASK_DEBUG=False
```

### **Bước 4: Install Dependencies (3 phút)**

**Nếu có SSH access:**
```bash
ssh your_username@qllhttbb.vn
cd public_html/
python3 -m pip install --user -r requirements_cpanel.txt
```

**Nếu không có SSH:**
- **cPanel** → **Python App** → **Create App**
- **Install packages** từ requirements_cpanel.txt

### **Bước 5: Initialize Database (2 phút)**

```bash
# SSH hoặc Python App terminal:
export FLASK_APP=app.py
python3 -m flask db upgrade

# Tạo admin user:
python3 -c "
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    admin = User(username='admin', email='admin@qllhttbb.vn', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print('Admin user created!')
"
```

---

## 🎉 **Done! Test Your Website**

### **URL**: https://qllhttbb.vn
### **Login**: 
- **Username**: `admin`
- **Password**: `admin123`

---

## 🔧 **Nếu gặp lỗi:**

### **1. Internal Server Error 500**
- **Check**: File permissions (644 for files, 755 for folders)
- **Check**: Python version support
- **Check**: Error logs trong cPanel

### **2. Database Connection Error**
- **Verify**: Database credentials trong `.env`
- **Check**: Database user permissions
- **Test**: Database connection trong cPanel

### **3. Python App không start**
- **Check**: `passenger_wsgi.py` file exists
- **Verify**: Python version compatibility
- **Install**: Missing dependencies

---

## 📋 **File Structure Check**

Đảm bảo structure như sau trong `public_html/`:

```
public_html/
├── app/                    ✅
├── migrations/             ✅
├── .env                    ✅ (tạo manual)
├── .htaccess              ✅
├── passenger_wsgi.py       ✅
├── app.py                 ✅
├── config.py              ✅
└── requirements_cpanel.txt ✅
```

---

## 🎯 **Test Checklist**

- ✅ **Website loads**: https://qllhttbb.vn
- ✅ **Login works**: admin/admin123
- ✅ **Dashboard shows**: Statistics và navigation
- ✅ **Database connected**: No connection errors
- ✅ **Static files load**: CSS/JS working properly

---

## 📞 **Need Help?**

1. **Check hosting docs** cho Python/Flask support
2. **Contact hosting support** về Python app setup
3. **Check cPanel error logs**
4. **Verify database connection**

---

**🎉 Vietnamese Classroom Management System live tại: https://qllhttbb.vn**

**Total setup time: ~15 minutes**
