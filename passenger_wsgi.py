#!/usr/bin/python3
import sys
import os

# Add your project directory to sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

# Create the Flask application
application = create_app()

if __name__ == "__main__":
    application.run()
