# 🚂 Deploy Vietnamese Classroom Management System lên Railway

## 🎯 **Tại sao chọn Railway?**

- ✅ **Dễ sử dụng**: Chỉ cần connect GitHub repo
- ✅ **Auto-deploy**: Tự động deploy khi có commit mới
- ✅ **Free tier**: $5 credit mỗi tháng (đủ cho small projects)
- ✅ **PostgreSQL**: Database miễn phí
- ✅ **Modern platform**: Interface đẹp, performance tốt

---

## 🚀 **Hướng dẫn Deploy (Step-by-step)**

### **Bước 1: Push code lên GitHub**

```bash
# Nếu chưa có GitHub repo, tạo repo mới trên GitHub
# Sau đó add remote và push:

git remote add origin https://github.com/your-username/vietnamese-classroom-management.git
git branch -M main
git push -u origin main
```

### **Bước 2: Tạo tài khoản Railway**

1. Đi tới **https://railway.app**
2. Click **"Login"** → **"Login with GitHub"**
3. Authorize Railway access to GitHub

### **Bước 3: Deploy Web Service**

1. **Click "New Project"**
2. **Select "Deploy from GitHub repo"**
3. **Choose repository**: `vietnamese-classroom-management`
4. **Railway sẽ tự động:**
   - Detect Python project
   - Install dependencies từ `requirements.txt`
   - Use `Procfile` để start app

### **Bước 4: Add PostgreSQL Database**

1. **Trong project dashboard, click "New"**
2. **Select "Database" → "Add PostgreSQL"**
3. **Railway sẽ tự động:**
   - Tạo PostgreSQL instance
   - Generate `DATABASE_URL`
   - Connect với web service

### **Bước 5: Configure Environment Variables**

1. **Click vào Web Service**
2. **Go to "Variables" tab**
3. **Add các variables sau:**

```bash
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
FLASK_ENV=production
FLASK_DEBUG=False
```

**Lưu ý**: `DATABASE_URL` sẽ được Railway tự động set!

### **Bước 6: Deploy và Setup Database**

1. **Railway sẽ tự động deploy**
2. **Sau khi deploy xong, setup database:**

Click **"Deploy Logs"** → Khi deploy xong, click **"Open App"**

### **Bước 7: Initialize Database (Important!)**

Railway không tự động chạy migrations. Cần setup database:

1. **Go to project dashboard**
2. **Click vào Web Service → "Deploy" tab**
3. **Scroll down và click "One-off Command"**
4. **Run command:**

```bash
flask db upgrade
```

5. **Tạo admin user (Optional):**

```bash
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
```

---

## 🎯 **Sau khi Deploy thành công**

### **Test Application**

1. **Click "Open App" để mở website**
2. **Login với admin account:**
   - Username: `admin`
   - Password: `admin123`

3. **Test các tính năng chính:**
   - ✅ Dashboard loading
   - ✅ User management
   - ✅ Class management
   - ✅ Schedule creation
   - ✅ Financial management
   - ✅ Notification generator

### **Custom Domain (Optional)**

1. **Go to "Settings" tab**
2. **Click "Domains"**
3. **Add custom domain** (cần verify DNS)

---

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **1. Application Error 500**
```bash
# Check logs trong Railway dashboard
# Thường do missing environment variables
```

#### **2. Database Connection Error**
```bash
# Đảm bảo PostgreSQL service đang chạy
# Check DATABASE_URL trong Variables tab
```

#### **3. Static Files không load**
```bash
# Railway tự động serve static files
# Đảm bảo Procfile đúng: web: gunicorn app:app
```

#### **4. Migration Error**
```bash
# Run trong One-off Command:
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## 📊 **Railway Dashboard Features**

### **Monitoring:**
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: History và rollback

### **Scaling:**
- **Auto-scaling**: Tự động scale theo traffic
- **Resource limits**: Set CPU/Memory limits

### **Collaboration:**
- **Team access**: Invite team members
- **Environment separation**: Dev/Staging/Production

---

## 💰 **Pricing & Limits**

### **Free Tier:**
- **$5 credit/month** (reset monthly)
- **Shared CPU/Memory**
- **500MB PostgreSQL storage**
- **Perfect cho development và small projects**

### **Pro Plan:**
- **$20/month** unlimited usage
- **Dedicated resources**
- **Priority support**

---

## 🎉 **Advantages của Railway**

1. **Zero Configuration**: Tự động detect và deploy
2. **Git Integration**: Auto-deploy từ GitHub
3. **Modern UI**: Dashboard đẹp và dễ sử dụng
4. **Fast Deployments**: Deploy nhanh hơn Heroku
5. **Built-in Database**: PostgreSQL integrated
6. **Environment Variables**: Easy management
7. **Custom Domains**: Free SSL certificates
8. **Team Collaboration**: Multi-user support

---

## 📞 **Support**

- **Railway Docs**: https://docs.railway.app
- **Discord Community**: https://discord.gg/railway
- **GitHub Issues**: Cho project-specific problems

---

**🎉 Chúc mừng! Vietnamese Classroom Management System đã live trên Railway!**

**URL sẽ có dạng**: `https://your-project-name.up.railway.app`
