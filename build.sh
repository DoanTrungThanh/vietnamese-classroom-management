#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "🚀 Starting build process for Vietnamese Classroom Management..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements_render.txt

echo "🗄️ Running database migrations..."
python -m flask db upgrade

echo "👤 Creating default admin user..."
python -c "
import os
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Check if admin user already exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@qllhttbb.vn',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created: admin/admin123')
    else:
        print('✅ Admin user already exists')
"

echo "✅ Build completed successfully!"
