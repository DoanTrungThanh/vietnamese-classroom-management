import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database configuration with support for multiple platforms
    database_url = os.environ.get('DATABASE_URL')

    # Handle different database URL formats
    if database_url:
        if database_url.startswith('postgres://'):
            # Railway/Render uses postgres:// but SQLAlchemy 1.4+ requires postgresql://
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        elif database_url.startswith('mysql://'):
            # cPanel MySQL support
            database_url = database_url.replace('mysql://', 'mysql+pymysql://', 1)

    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False  # Disable CSRF protection temporarily

    # Pagination
    POSTS_PER_PAGE = 25

    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Railway specific settings
    PORT = int(os.environ.get('PORT', 5000))
