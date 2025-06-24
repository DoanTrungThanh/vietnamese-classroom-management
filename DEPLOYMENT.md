# 🚀 Hướng dẫn Deploy Vietnamese Classroom Management System

## ⚠️ Lưu ý quan trọng
**GitHub Pages không hỗ trợ Flask applications**. Dự án này cần server để chạy backend Python.

## 🎯 Các platform deployment được khuyến nghị:

### 1. **Heroku (Khuyến nghị - Free tier)**
### 2. **Railway (Modern, dễ sử dụng)**
### 3. **Render (Free tier với PostgreSQL)**
### 4. **PythonAnywhere (Chuyên Python)**

---

## 🚀 Deploy lên Heroku (Chi tiết)

### **Bước 1: Cài đặt Heroku CLI**
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Windows
# Download từ: https://devcenter.heroku.com/articles/heroku-cli

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

### **Bước 2: Login Heroku**
```bash
heroku login
```

### **Bước 3: Tạo Git repository (nếu chưa có)**
```bash
git init
git add .
git commit -m "Initial commit - Vietnamese Classroom Management System"
```

### **Bước 4: Tạo Heroku app**
```bash
# Tạo app với tên unique
heroku create your-classroom-app-name

# Hoặc để Heroku tự tạo tên
heroku create
```

### **Bước 5: Cấu hình environment variables**
```bash
# Set secret key
heroku config:set SECRET_KEY="your-super-secret-key-here"

# Set Flask environment
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=False

# Heroku sẽ tự động set DATABASE_URL cho PostgreSQL
```

### **Bước 6: Add PostgreSQL database**
```bash
# Add free PostgreSQL addon
heroku addons:create heroku-postgresql:mini
```

### **Bước 7: Deploy**
```bash
# Push code lên Heroku
git push heroku main

# Chạy database migrations
heroku run flask db upgrade

# Tạo admin user (optional)
heroku run python -c "
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    admin = User(username='admin', email='admin@example.com', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print('Admin user created!')
"
```

### **Bước 8: Mở ứng dụng**
```bash
heroku open
```

---

## 🚀 Deploy lên Railway (Đơn giản)

### **Bước 1: Tạo account tại railway.app**

### **Bước 2: Connect GitHub repository**
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose repository này

### **Bước 3: Cấu hình environment variables**
```
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False
```

### **Bước 4: Add PostgreSQL database**
1. Click "New" → "Database" → "PostgreSQL"
2. Railway sẽ tự động set DATABASE_URL

### **Bước 5: Deploy tự động**
Railway sẽ tự động deploy khi có commit mới!

---

## 🚀 Deploy lên Render

### **Bước 1: Tạo account tại render.com**

### **Bước 2: Tạo Web Service**
1. Click "New" → "Web Service"
2. Connect GitHub repository
3. Cấu hình:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### **Bước 3: Add PostgreSQL database**
1. Click "New" → "PostgreSQL"
2. Copy DATABASE_URL vào environment variables

### **Bước 4: Cấu hình environment variables**
```
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=postgresql://...
```

---

## 📋 Checklist trước khi deploy

- ✅ **Procfile** đã tạo
- ✅ **requirements.txt** đã tạo
- ✅ **runtime.txt** đã tạo
- ✅ **Config.py** hỗ trợ environment variables
- ✅ **Database migrations** đã sẵn sàng
- ✅ **Secret key** đã được set
- ✅ **Debug mode** đã tắt cho production

## 🔧 Troubleshooting

### **Lỗi thường gặp:**

1. **Application error**
   ```bash
   heroku logs --tail
   ```

2. **Database connection error**
   ```bash
   heroku config:get DATABASE_URL
   heroku run flask db upgrade
   ```

3. **Static files không load**
   - Kiểm tra Procfile
   - Đảm bảo gunicorn đã cài đặt

## 🎯 Sau khi deploy thành công

1. **Tạo admin user**
2. **Test tất cả tính năng**
3. **Backup database định kỳ**
4. **Monitor logs**

## 📞 Support

Nếu gặp vấn đề, check:
1. Heroku logs: `heroku logs --tail`
2. Database status: `heroku pg:info`
3. Config vars: `heroku config`

---

**🎉 Chúc mừng! Hệ thống Vietnamese Classroom Management đã sẵn sàng cho production!**
