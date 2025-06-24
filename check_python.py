#!/usr/bin/env python3
"""
Script to check Python environment on hosting
Upload this file and run via browser to check Python support
"""

import sys
import os
import subprocess

print("Content-Type: text/html\n")
print("<html><head><title>Python Environment Check</title></head><body>")
print("<h1>Python Environment Check for qllhttbb.vn</h1>")

print("<h2>Python Version:</h2>")
print(f"<p>Python {sys.version}</p>")

print("<h2>Python Executable:</h2>")
print(f"<p>{sys.executable}</p>")

print("<h2>Python Path:</h2>")
print("<ul>")
for path in sys.path:
    print(f"<li>{path}</li>")
print("</ul>")

print("<h2>Environment Variables:</h2>")
print("<ul>")
for key, value in os.environ.items():
    if 'PYTHON' in key or 'PATH' in key:
        print(f"<li><strong>{key}:</strong> {value}</li>")
print("</ul>")

print("<h2>Available Modules:</h2>")
try:
    import flask
    print(f"<p>✅ Flask: {flask.__version__}</p>")
except ImportError:
    print("<p>❌ Flask not available</p>")

try:
    import sqlalchemy
    print(f"<p>✅ SQLAlchemy: {sqlalchemy.__version__}</p>")
except ImportError:
    print("<p>❌ SQLAlchemy not available</p>")

print("<h2>CGI Support Test:</h2>")
print("<p>If you can see this page, CGI is working!</p>")

print("</body></html>")
