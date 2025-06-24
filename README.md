# 🎓 Vietnamese Classroom Management System

Hệ thống quản lý lớp học tiếng Việt hoàn chỉnh với Flask và Tailwind CSS.

## ✨ Tính năng chính

### 👥 **Quản lý người dùng (3 roles)**
- **Admin**: Quản lý toàn bộ hệ thống
- **Manager (Quản sinh)**: Quản lý lớp học và lịch dạy
- **Teacher (Giáo viên)**: Xem lịch và điểm danh

### 📚 **Quản lý lớp học**
- ✅ CRUD lớp học hoàn chỉnh
- ✅ Thêm/xóa học sinh khỏi lớp
- ✅ Quản lý thông tin chi tiết lớp học

### 📅 **Quản lý lịch dạy**
- ✅ **Week-based scheduling**: Lịch theo tuần cụ thể
- ✅ **Copy schedule**: Sao chép lịch giữa các tuần
- ✅ **Multiple time slots**: Sáng, chiều, tối
- ✅ **Calendar views**: Weekly và Monthly
- ✅ **Schedule deletion**: Xóa lịch trực tiếp từ calendar

### 👨‍🎓 **Quản lý học sinh**
- ✅ **Auto student codes**: Mã học sinh tự động từ 1000
- ✅ **Many-to-many relationship**: Học sinh học nhiều môn
- ✅ **Workflow**: Thêm học sinh → Assign vào lớp → Enroll vào lịch

### 📊 **Điểm danh và thống kê**
- ✅ Điểm danh theo ngày và lớp
- ✅ Dashboard với thống kê tổng quan
- ✅ Báo cáo attendance

### 💰 **Quản lý tài chính**
- ✅ **Income/Expense tracking**
- ✅ **Donation management**: Nhận và phân phối tài sản
- ✅ **Financial dashboard**: Thống kê thu chi
- ✅ **Transaction history**: Lịch sử giao dịch

### 📱 **Notification system**
- ✅ **Template generator**: Tạo thông báo cho phụ huynh
- ✅ **Multiple templates**: Daily, weekly, reminder, event
- ✅ **Enhanced date picker**: Quick date selection
- ✅ **Copy/Download**: Sao chép và tải về thông báo

## 🎨 **UI/UX Features**

- ✅ **Tailwind CSS**: Modern, responsive design
- ✅ **White-orange theme**: Professional color scheme
- ✅ **Mobile-friendly**: Responsive trên mọi thiết bị
- ✅ **Interactive components**: Modals, dropdowns, animations
- ✅ **Dashboard**: Comprehensive overview với charts

## 🚀 **Tech Stack**

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: Tailwind CSS, JavaScript
- **Database**: SQLite (dev), PostgreSQL (production)
- **Forms**: WTForms, Flask-WTF
- **Authentication**: Role-based access control

## 📦 **Installation**

### **Local Development**
```bash
# Clone repository
git clone <repository-url>
cd vietnamese-classroom-management

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set up database
flask db upgrade

# Create admin user
python -c "
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

# Run application
flask run
```

### **Production Deployment**
Xem [DEPLOYMENT.md](DEPLOYMENT.md) để biết chi tiết deploy lên:
- Heroku (Khuyến nghị)
- Railway
- Render
- PythonAnywhere

## 👤 **Demo Accounts**

| Role | Username | Password | Permissions |
|------|----------|----------|-------------|
| Admin | admin | admin123 | Full system access |
| Manager | manager | manager123 | Class & schedule management |
| Teacher | teacher | teacher123 | View schedule & attendance |

## 🔧 **Configuration**

### **Environment Variables**
```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
FLASK_ENV=development
FLASK_DEBUG=True
```

## 📞 **Support**

Nếu gặp vấn đề hoặc có câu hỏi:
1. Check [DEPLOYMENT.md](DEPLOYMENT.md) cho deployment issues
2. Create GitHub issue
3. Contact: [your-email@example.com]

---

**🎉 Vietnamese Classroom Management System - Phiên bản 1.0 - Production Ready!**
# vietnamese-classroom-management
