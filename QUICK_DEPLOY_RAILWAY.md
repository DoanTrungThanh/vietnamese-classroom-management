# ⚡ Quick Deploy to Railway - 5 Minutes Setup

## 🚀 **Super Fast Deployment Steps**

### **1. Push to GitHub (2 minutes)**
```bash
# Create new repo on GitHub: vietnamese-classroom-management
# Then run:
git remote add origin https://github.com/YOUR_USERNAME/vietnamese-classroom-management.git
git branch -M main
git push -u origin main
```

### **2. Deploy on Railway (2 minutes)**
1. Go to **https://railway.app**
2. **Login with GitHub**
3. **New Project** → **Deploy from GitHub repo**
4. **Select**: `vietnamese-classroom-management`
5. **Wait for auto-deploy** ⏳

### **3. Add Database (30 seconds)**
1. **Click "New"** → **Database** → **Add PostgreSQL**
2. **Railway auto-connects** database to web service ✅

### **4. Set Environment Variables (30 seconds)**
1. **Click Web Service** → **Variables tab**
2. **Add**:
   ```
   SECRET_KEY=your-super-secret-key-make-it-long-and-random
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

### **5. Initialize Database (1 minute)**
1. **Web Service** → **Deploy tab** → **One-off Command**
2. **Run**: `flask db upgrade`
3. **Create admin** (optional):
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
       print('Admin created!')
   "
   ```

## 🎉 **Done! Your app is live!**

**Click "Open App"** → Login with `admin/admin123`

---

## 📋 **Checklist**

- ✅ Code pushed to GitHub
- ✅ Railway project created
- ✅ PostgreSQL database added
- ✅ Environment variables set
- ✅ Database initialized
- ✅ Admin user created
- ✅ App is live and working!

---

## 🔗 **Your app URL**: 
`https://your-project-name.up.railway.app`

## 👤 **Login credentials**:
- **Username**: `admin`
- **Password**: `admin123`

---

## 🆘 **If something goes wrong**:

1. **Check Deploy Logs** in Railway dashboard
2. **Verify Environment Variables** are set correctly
3. **Ensure Database** is connected and running
4. **Run migrations** if database errors occur

**Need help?** Check [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for detailed troubleshooting.

---

**🎯 Total time: ~5 minutes for full deployment!**
