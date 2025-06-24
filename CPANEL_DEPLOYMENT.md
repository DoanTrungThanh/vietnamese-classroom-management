# 🏠 Deploy Vietnamese Classroom Management lên cPanel Hosting

## 📋 **Yêu cầu hosting**

- ✅ **Python 3.8+** support
- ✅ **MySQL/PostgreSQL** database
- ✅ **SSH access** (khuyến nghị)
- ✅ **File Manager** access
- ✅ **Subdomain/Domain** setup

---

## 🚀 **Hướng dẫn Deploy (Step-by-step)**

### **Bước 1: Chuẩn bị Database**

1. **Login vào cPanel** → **MySQL Databases**
2. **Tạo database mới**:
   - Database name: `qllhttbb_classroom`
   - Username: `qllhttbb_admin`
   - Password: `strong_password_here`
3. **Assign user to database** với **ALL PRIVILEGES**
4. **Ghi nhớ thông tin**:
   ```
   Database: qllhttbb_classroom
   Username: qllhttbb_admin
   Password: your_password
   Host: localhost
   ```

### **Bước 2: Upload Files**

#### **Option A: File Manager (Dễ nhất)**

1. **cPanel** → **File Manager**
2. **Navigate** to `public_html/` (hoặc domain folder)
3. **Upload** toàn bộ project files:
   - Zip toàn bộ project
   - Upload zip file
   - Extract trong `public_html/`

#### **Option B: FTP/SFTP**

```bash
# Sử dụng FileZilla hoặc WinSCP
Host: qllhttbb.vn
Username: your_cpanel_username
Password: your_cpanel_password
Port: 21 (FTP) hoặc 22 (SFTP)

# Upload toàn bộ files vào public_html/
```

### **Bước 3: Cấu hình Environment Variables**

Tạo file `.env` trong `public_html/`:

```bash
SECRET_KEY=your-super-secret-key-for-production
DATABASE_URL=mysql://qllhttbb_admin:your_password@localhost/qllhttbb_classroom
FLASK_ENV=production
FLASK_DEBUG=False
```

### **Bước 4: Install Dependencies**

#### **Nếu có SSH access:**

```bash
# SSH vào hosting
ssh your_username@qllhttbb.vn

# Navigate to project directory
cd public_html/

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements_cpanel.txt
```

#### **Nếu không có SSH:**

1. **cPanel** → **Python App** (nếu có)
2. **Create Python App**
3. **Install packages** từ requirements_cpanel.txt

### **Bước 5: Setup Database**

```bash
# Trong SSH hoặc Python App terminal:
export FLASK_APP=app.py
flask db upgrade

# Tạo admin user
python -c "
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

### **Bước 6: Configure Web Server**

#### **Nếu hosting hỗ trợ Python Apps:**

1. **cPanel** → **Setup Python App**
2. **Application root**: `/public_html/`
3. **Application URL**: `qllhttbb.vn`
4. **Application startup file**: `passenger_wsgi.py`
5. **Python version**: 3.8+

#### **Nếu chỉ có CGI support:**

Cần modify `app.py` để chạy như CGI script.

---

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **1. Internal Server Error 500**
```bash
# Check error logs trong cPanel
# Thường do:
- Python version không đúng
- Missing dependencies
- Database connection error
- File permissions
```

#### **2. Database Connection Error**
```bash
# Kiểm tra:
- Database credentials trong .env
- Database user permissions
- Host name (localhost vs IP)
```

#### **3. Static Files không load**
```bash
# Đảm bảo:
- .htaccess file đúng
- File permissions 644 cho files, 755 cho folders
- Static files trong đúng thư mục
```

#### **4. Python Import Errors**
```bash
# Install missing packages:
pip install package_name

# Hoặc update requirements_cpanel.txt
```

---

## 📁 **File Structure trên hosting**

```
public_html/
├── app/                    # Flask application
├── migrations/             # Database migrations
├── static/                 # Static files (CSS, JS, images)
├── templates/              # HTML templates
├── .env                    # Environment variables
├── .htaccess              # Apache configuration
├── passenger_wsgi.py       # WSGI entry point
├── app.py                 # Main application file
├── config.py              # Configuration
├── requirements_cpanel.txt # Dependencies
└── instance/              # Instance folder
    └── app.db             # SQLite database (if used)
```

---

## 🔒 **Security Considerations**

### **File Permissions:**
```bash
# Set correct permissions
find public_html/ -type f -exec chmod 644 {} \;
find public_html/ -type d -exec chmod 755 {} \;
chmod 600 .env  # Protect environment file
```

### **Hide sensitive files:**
Add to `.htaccess`:
```apache
<Files ".env">
    Order allow,deny
    Deny from all
</Files>

<Files "config.py">
    Order allow,deny
    Deny from all
</Files>
```

---

## 🎯 **Post-Deployment Checklist**

- ✅ **Website loads**: https://qllhttbb.vn
- ✅ **Login works**: admin/admin123
- ✅ **Database connected**: Check dashboard stats
- ✅ **Static files load**: CSS/JS working
- ✅ **All features work**: Test major functionality
- ✅ **SSL certificate**: HTTPS enabled
- ✅ **Backup setup**: Regular database backups

---

## 📞 **Support**

**Nếu gặp vấn đề:**
1. **Check hosting documentation** cho Python support
2. **Contact hosting support** về Python/Flask setup
3. **Check error logs** trong cPanel
4. **Test locally** trước khi deploy

---

**🎉 Vietnamese Classroom Management System sẽ live tại: https://qllhttbb.vn**
