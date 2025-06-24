#!/usr/bin/env python3
"""
CGI entry point for Vietnamese Classroom Management System
"""

import sys
import os
import cgitb

# Enable CGI error reporting
cgitb.enable()

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    # Import Flask app
    from app import create_app
    from wsgiref.handlers import CGIHandler
    
    # Create Flask application
    app = create_app()
    
    # Run via CGI
    CGIHandler().run(app)
    
except Exception as e:
    print("Content-Type: text/html\n")
    print(f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>")
