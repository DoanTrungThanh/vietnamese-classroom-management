#!/usr/bin/env python3
"""
Export static HTML version of Vietnamese Classroom Management System
for hosting that doesn't support Python
"""
import os
import shutil
import zipfile
from datetime import datetime

def export_static_version():
    """Export static HTML files"""

    print("🚀 Creating static HTML version for cPanel hosting...")

    # Create static export directory
    static_dir = "static_export"
    if os.path.exists(static_dir):
        shutil.rmtree(static_dir)
    os.makedirs(static_dir)

    # Copy static assets
    if os.path.exists("app/static"):
        shutil.copytree("app/static", f"{static_dir}/static")
        print("✅ Copied static assets")

    # Create basic HTML structure
    create_static_html(static_dir)

    # Create zip file for easy upload
    create_zip_package(static_dir)

    print(f"✅ Static version created in: {static_dir}/")
    print("📁 Upload contents to public_html/ on your hosting")
    
def create_static_html(static_dir):
    """Create static HTML files"""
    
    # Main index.html
    index_html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hệ thống Quản lý Lớp học Tiếng Việt</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body class="bg-gray-50">
    <div class="min-h-screen flex items-center justify-center">
        <div class="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
            <div class="text-center mb-8">
                <div class="mx-auto w-16 h-16 bg-orange-500 rounded-full flex items-center justify-center mb-4">
                    <i class="fas fa-graduation-cap text-white text-2xl"></i>
                </div>
                <h1 class="text-3xl font-bold text-gray-900 mb-2">Hệ thống Quản lý Lớp học</h1>
                <p class="text-gray-600">Phiên bản Demo - Static HTML</p>
            </div>
            
            <div class="space-y-4">
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h3 class="font-semibold text-blue-800 mb-2">
                        <i class="fas fa-info-circle mr-2"></i>
                        Thông báo quan trọng
                    </h3>
                    <p class="text-blue-700 text-sm">
                        Hosting của bạn không hỗ trợ Python/Flask applications. 
                        Đây là phiên bản demo tĩnh để xem giao diện.
                    </p>
                </div>
                
                <div class="grid grid-cols-2 gap-4">
                    <a href="dashboard.html" class="bg-orange-500 hover:bg-orange-600 text-white p-4 rounded-lg text-center transition-colors">
                        <i class="fas fa-tachometer-alt block text-2xl mb-2"></i>
                        <span class="text-sm">Dashboard</span>
                    </a>
                    <a href="classes.html" class="bg-blue-500 hover:bg-blue-600 text-white p-4 rounded-lg text-center transition-colors">
                        <i class="fas fa-chalkboard-teacher block text-2xl mb-2"></i>
                        <span class="text-sm">Lớp học</span>
                    </a>
                    <a href="schedule.html" class="bg-green-500 hover:bg-green-600 text-white p-4 rounded-lg text-center transition-colors">
                        <i class="fas fa-calendar-alt block text-2xl mb-2"></i>
                        <span class="text-sm">Lịch dạy</span>
                    </a>
                    <a href="financial.html" class="bg-purple-500 hover:bg-purple-600 text-white p-4 rounded-lg text-center transition-colors">
                        <i class="fas fa-money-bill-wave block text-2xl mb-2"></i>
                        <span class="text-sm">Tài chính</span>
                    </a>
                </div>
                
                <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <h3 class="font-semibold text-yellow-800 mb-2">
                        <i class="fas fa-lightbulb mr-2"></i>
                        Để có đầy đủ tính năng
                    </h3>
                    <p class="text-yellow-700 text-sm mb-2">
                        Bạn cần hosting hỗ trợ Python hoặc sử dụng:
                    </p>
                    <ul class="text-yellow-700 text-sm space-y-1">
                        <li>• Railway.app (miễn phí)</li>
                        <li>• Heroku (miễn phí)</li>
                        <li>• Render.com (miễn phí)</li>
                        <li>• PythonAnywhere</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    with open(f"{static_dir}/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    
    # Create other demo pages
    create_demo_pages(static_dir)

def create_demo_pages(static_dir):
    """Create demo pages"""
    
    pages = {
        "dashboard.html": "Dashboard Demo",
        "classes.html": "Quản lý Lớp học",
        "schedule.html": "Lịch dạy",
        "financial.html": "Quản lý Tài chính"
    }
    
    for filename, title in pages.items():
        html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Demo</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body class="bg-gray-50">
    <div class="min-h-screen">
        <nav class="bg-white shadow-sm border-b">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between h-16">
                    <div class="flex items-center">
                        <a href="index.html" class="text-orange-600 hover:text-orange-700">
                            <i class="fas fa-arrow-left mr-2"></i>
                            Về trang chủ
                        </a>
                    </div>
                    <div class="flex items-center">
                        <h1 class="text-xl font-semibold text-gray-900">{title}</h1>
                    </div>
                </div>
            </div>
        </nav>
        
        <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div class="bg-white rounded-lg shadow p-6">
                <div class="text-center py-12">
                    <i class="fas fa-code text-6xl text-gray-300 mb-4"></i>
                    <h2 class="text-2xl font-bold text-gray-900 mb-4">Demo Interface</h2>
                    <p class="text-gray-600 mb-6">
                        Đây là giao diện demo cho {title.lower()}.<br>
                        Để có đầy đủ tính năng, cần hosting hỗ trợ Python/Flask.
                    </p>
                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto">
                        <h3 class="font-semibold text-blue-800 mb-2">Tính năng thực tế sẽ bao gồm:</h3>
                        <ul class="text-blue-700 text-sm text-left space-y-1">
                            <li>• CRUD operations đầy đủ</li>
                            <li>• Database integration</li>
                            <li>• User authentication</li>
                            <li>• Real-time updates</li>
                            <li>• Export/Import data</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
        
        with open(f"{static_dir}/{filename}", "w", encoding="utf-8") as f:
            f.write(html_content)

def create_zip_package(static_dir):
    """Create zip package for easy upload"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"qllhttbb_static_{timestamp}.zip"

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(static_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, static_dir)
                zipf.write(file_path, arcname)

    print(f"📦 Created zip package: {zip_filename}")
    return zip_filename

if __name__ == "__main__":
    export_static_version()
