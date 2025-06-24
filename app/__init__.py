from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
csrf = CSRFProtect()
login.login_view = 'auth.login'
login.login_message = 'Vui lòng đăng nhập để truy cập trang này.'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)  # Enable CSRF protection

    # Add CSRF token to template context
    @app.context_processor
    def inject_csrf_token():
        try:
            from flask_wtf.csrf import generate_csrf
            return dict(csrf_token=generate_csrf)
        except:
            return dict(csrf_token='')

    from app.routes import main, auth, admin, manager, teacher, user, finance, calendar, expense, financial, api
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(manager.bp, url_prefix='/manager')
    app.register_blueprint(teacher.bp, url_prefix='/teacher')
    app.register_blueprint(user.bp, url_prefix='/user')
    app.register_blueprint(finance.bp, url_prefix='/finance')
    app.register_blueprint(calendar.bp, url_prefix='/calendar')
    app.register_blueprint(expense.bp, url_prefix='/expense')
    app.register_blueprint(financial.bp)
    app.register_blueprint(api.bp)

    return app

from app import models
