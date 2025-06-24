# 🔧 Manual cPanel Deployment - Vietnamese Classroom Management

## ⚠️ **Cho hosting KHÔNG có Python App installer**

Hosting của bạn không có giao diện Python App, cần deploy thủ công qua CGI.

---

## 📋 **Yêu cầu hosting**

- ✅ **CGI support** (hầu hết hosting đều có)
- ✅ **Python 3.6+** installed
- ✅ **MySQL database** access
- ✅ **File Manager** hoặc FTP access

---

## 🚀 **Hướng dẫn Deploy Manual (20 phút)**

### **Bước 1: Test Python Support (2 phút)**

1. **Upload** `check_python.py` vào `public_html/`
2. **Set permissions**: `chmod 755 check_python.py`
3. **Visit**: `https://qllhttbb.vn/check_python.py`
4. **Check output** để xem Python version và modules

### **Bước 2: Setup Database (3 phút)**

1. **cPanel** → **MySQL Databases**
2. **Create Database**: `qllhttbb_classroom`
3. **Create User**: 
   - Username: `qllhttbb_admin`
   - Password: `ClassRoom2024!`
4. **Add User to Database** → **ALL PRIVILEGES**

### **Bước 3: Upload Application Files (5 phút)**

1. **Download** deployment package
2. **cPanel** → **File Manager** → `public_html/`
3. **Upload** và **extract** zip file
4. **Upload** thêm `index.cgi` và `check_python.py`

### **Bước 4: Set File Permissions (2 phút)**

**Via File Manager:**
```
index.cgi → 755
check_python.py → 755
app/ → 755 (folder)
All .py files → 644
```

**Via SSH (nếu có):**
```bash
chmod 755 index.cgi check_python.py
chmod -R 755 app/
find . -name "*.py" -exec chmod 644 {} \;
```

### **Bước 5: Configure Environment (3 phút)**

**Tạo file `.env`** trong `public_html/`:

```bash
SECRET_KEY=QllhTtbb2024SuperSecretKeyForProduction
DATABASE_URL=mysql://qllhttbb_admin:ClassRoom2024!@localhost/qllhttbb_classroom
FLASK_ENV=production
FLASK_DEBUG=False
```

### **Bước 6: Install Dependencies Manual (5 phút)**

**Nếu có SSH:**
```bash
# Install to user directory
python3 -m pip install --user Flask==2.3.3
python3 -m pip install --user Flask-SQLAlchemy==3.0.5
python3 -m pip install --user Flask-Login==0.6.3
python3 -m pip install --user Flask-WTF==1.1.1
python3 -m pip install --user Flask-Migrate==4.1.0
python3 -m pip install --user PyMySQL
```

**Nếu KHÔNG có SSH:**
- Contact hosting support để install packages
- Hoặc sử dụng local installation (copy site-packages)

### **Bước 7: Initialize Database (Manual)**

**Tạo file `init_db.py`:**

```python
#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Create tables
    db.create_all()
    
    # Create admin user
    admin = User(username='admin', email='admin@qllhttbb.vn', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    
    print("Database initialized and admin user created!")
```

**Run via browser**: `https://qllhttbb.vn/init_db.py`

---

## 🔧 **Alternative: Static HTML Version**

Nếu Python không hoạt động, tạo static HTML version:

### **Tạo simple HTML interface:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Vietnamese Classroom Management</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto p-8">
        <h1 class="text-3xl font-bold text-center mb-8">
            Hệ thống Quản lý Lớp học
        </h1>
        <div class="bg-white p-6 rounded-lg shadow">
            <p class="text-center text-gray-600">
                Hệ thống đang được cài đặt...
            </p>
            <p class="text-center mt-4">
                <a href="mailto:admin@qllhttbb.vn" class="text-blue-500">
                    Liên hệ admin để được hỗ trợ
                </a>
            </p>
        </div>
    </div>
</body>
</html>
```

---

## 🆘 **Troubleshooting**

### **1. CGI Script Error**
```bash
# Check error logs trong cPanel
# Common issues:
- Wrong file permissions (should be 755)
- Python path incorrect
- Missing shebang line (#!/usr/bin/env python3)
```

### **2. Module Import Errors**
```bash
# Install missing modules:
python3 -m pip install --user module_name

# Or contact hosting support
```

### **3. Database Connection Error**
```bash
# Check:
- Database credentials
- MySQL service running
- User permissions
```

### **4. Permission Denied**
```bash
# Set correct permissions:
chmod 755 index.cgi
chmod 644 .env
chmod -R 755 app/
```

---

## 📞 **Contact Hosting Support**

Nếu gặp khó khăn, liên hệ hosting support với các câu hỏi:

1. **"Does hosting support Python CGI scripts?"**
2. **"How to install Python packages?"**
3. **"What Python version is available?"**
4. **"Can you help install Flask framework?"**

---

## 🎯 **Expected Results**

**Nếu thành công:**
- ✅ `https://qllhttbb.vn/check_python.py` shows Python info
- ✅ `https://qllhttbb.vn` loads application
- ✅ Login works with admin/admin123

**Nếu không thành công:**
- 📧 Contact hosting support
- 🔄 Consider upgrading to Python-friendly hosting
- 💡 Use static HTML placeholder

---

**⏱️ Total setup time: ~20 minutes (if Python is supported)**
