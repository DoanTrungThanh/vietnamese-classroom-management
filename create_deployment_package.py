#!/usr/bin/env python3
"""
Script to create deployment package for cPanel hosting
"""
import os
import zipfile
import shutil
from datetime import datetime

def create_deployment_package():
    """Create a zip file ready for cPanel deployment"""
    
    # Files and folders to include
    include_files = [
        'app/',
        'migrations/',
        'static/',
        'templates/',
        '.htaccess',
        'passenger_wsgi.py',
        'app.py',
        'config.py',
        'requirements_cpanel.txt',
        '.env.example'
    ]
    
    # Files to exclude
    exclude_patterns = [
        '__pycache__',
        '*.pyc',
        '.git',
        '.venv',
        'venv/',
        '*.db',
        '.env',
        'instance/',
        'DEPLOYMENT.md',
        'RAILWAY_DEPLOYMENT.md',
        'README.md'
    ]
    
    # Create timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"qllhttbb_deployment_{timestamp}.zip"
    
    print(f"Creating deployment package: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in include_files:
            if os.path.exists(item):
                if os.path.isfile(item):
                    zipf.write(item)
                    print(f"Added file: {item}")
                elif os.path.isdir(item):
                    for root, dirs, files in os.walk(item):
                        # Skip excluded directories
                        dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
                        
                        for file in files:
                            # Skip excluded files
                            if not any(pattern in file for pattern in exclude_patterns):
                                file_path = os.path.join(root, file)
                                zipf.write(file_path)
                                print(f"Added: {file_path}")
            else:
                print(f"Warning: {item} not found, skipping...")
    
    print(f"\n✅ Deployment package created: {zip_filename}")
    print(f"📦 File size: {os.path.getsize(zip_filename) / 1024 / 1024:.2f} MB")
    
    print("\n📋 Next steps:")
    print("1. Login to cPanel")
    print("2. Go to File Manager")
    print("3. Navigate to public_html/")
    print(f"4. Upload {zip_filename}")
    print("5. Extract the zip file")
    print("6. Follow CPANEL_DEPLOYMENT.md for setup")
    
    return zip_filename

if __name__ == "__main__":
    create_deployment_package()
