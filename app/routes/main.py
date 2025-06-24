from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models.user import User
from app.models.class_model import Class
from app.models.student import Student
from app.models.schedule import Schedule
from app.models.attendance import Attendance
from app.models.event import Event
from app.models.finance import Finance
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    from datetime import datetime, date

    # Redirect user role to their specific dashboard
    if current_user.is_user():
        return redirect(url_for('user.dashboard'))

    # Statistics for dashboard
    stats = {}
    today_schedules = []

    if current_user.is_admin():
        stats['total_classes'] = Class.query.filter_by(is_active=True).count()
        stats['total_students'] = Student.query.filter_by(is_active=True).count()
        stats['total_teachers'] = User.query.filter_by(role='teacher', is_active=True).count()
        stats['total_managers'] = User.query.filter_by(role='manager', is_active=True).count()

        # Get today's schedules for admin
        today = datetime.now()
        day_of_week = today.weekday() + 1  # Monday = 1
        today_schedules = Schedule.query.filter_by(
            day_of_week=day_of_week,
            is_active=True
        ).order_by(Schedule.session, Schedule.start_time).all()
        stats['today_schedules'] = len(today_schedules)

    elif current_user.is_manager():
        managed_classes = Class.query.filter_by(manager_id=current_user.id, is_active=True)
        stats['total_classes'] = managed_classes.count()
        stats['total_students'] = sum(c.student_count for c in managed_classes)
        stats['total_teachers'] = User.query.filter_by(role='teacher', is_active=True).count()

        # Get today's schedules for manager
        today = datetime.now()
        day_of_week = today.weekday() + 1  # Monday = 1
        managed_class_ids = [c.id for c in managed_classes]
        today_schedules = Schedule.query.filter(
            Schedule.class_id.in_(managed_class_ids),
            Schedule.day_of_week == day_of_week,
            Schedule.is_active == True
        ).order_by(Schedule.session, Schedule.start_time).all()
        stats['today_schedules'] = len(today_schedules)

    elif current_user.is_teacher():
        teaching_schedules = Schedule.query.filter_by(teacher_id=current_user.id, is_active=True)
        stats['teaching_classes'] = len(set(s.class_id for s in teaching_schedules))
        stats['weekly_sessions'] = teaching_schedules.count()
        stats['total_students'] = sum(s.class_obj.student_count for s in teaching_schedules)
        stats['total_teachers'] = User.query.filter_by(role='teacher', is_active=True).count()
        stats['total_classes'] = Class.query.filter_by(is_active=True).count()

        # Get today's schedules for teacher
        today = datetime.now()
        day_of_week = today.weekday() + 1  # Monday = 1
        today_schedules = Schedule.query.filter_by(
            teacher_id=current_user.id,
            day_of_week=day_of_week,
            is_active=True
        ).order_by(Schedule.session, Schedule.start_time).all()

        stats['today_schedules'] = len(today_schedules)

    # Recent activities
    recent_events = Event.query.filter_by(is_active=True).order_by(Event.created_at.desc()).limit(5).all()

    return render_template('dashboard_tailwind.html', title='Dashboard', stats=stats,
                         recent_events=recent_events, today_schedules=today_schedules)

@bp.route('/health')
def health_check():
    """Health check endpoint for Render"""
    try:
        # Simple database check
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'message': 'Vietnamese Classroom Management System is running',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'message': 'Database connection failed',
            'error': str(e)
        }), 500
