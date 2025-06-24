from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.models.student import Student
from app.models.class_model import Class
from functools import wraps

bp = Blueprint('api', __name__, url_prefix='/api')

def admin_or_manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_admin() or current_user.is_manager()):
            return jsonify({'error': 'Unauthorized'}), 403
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/students')
@login_required
@admin_or_manager_required
def get_students():
    """Get all students for dropdown selection"""
    students = Student.query.filter_by(is_active=True).order_by(Student.full_name).all()
    
    return jsonify([{
        'id': student.id,
        'full_name': student.full_name,
        'student_code': student.student_code
    } for student in students])

@bp.route('/classes')
@login_required
@admin_or_manager_required
def get_classes():
    """Get all classes for dropdown selection"""
    classes = Class.query.filter_by(is_active=True).order_by(Class.name).all()
    
    return jsonify([{
        'id': cls.id,
        'name': cls.name,
        'subject': cls.subject
    } for cls in classes])

@bp.route('/students/<int:class_id>')
@login_required
@admin_or_manager_required
def get_students_by_class(class_id):
    """Get students in a specific class"""
    class_obj = Class.query.get_or_404(class_id)
    students = class_obj.students.filter_by(is_active=True).order_by(Student.full_name).all()

    return jsonify([{
        'id': student.id,
        'full_name': student.full_name,
        'student_code': student.student_code
    } for student in students])

@bp.route('/schedules/preview')
@login_required
@admin_or_manager_required
def get_schedules_preview():
    """Get schedules for preview in copy function"""
    from flask import request
    from app.models.schedule import Schedule

    week = request.args.get('week')
    if not week:
        return jsonify({'success': False, 'message': 'Week parameter required'})

    try:
        # Get schedules for the specified week
        schedules = Schedule.query.filter_by(
            week_number=week,
            is_active=True
        ).order_by(Schedule.day_of_week, Schedule.start_time).all()

        # Filter by manager permission if not admin
        if not current_user.is_admin():
            schedules = [s for s in schedules if s.class_obj.manager_id == current_user.id]

        schedule_data = []
        for schedule in schedules:
            schedule_data.append({
                'id': schedule.id,
                'class_name': schedule.class_obj.name,
                'teacher_name': schedule.teacher.full_name,
                'day_of_week': schedule.day_of_week,
                'start_time': schedule.start_time.strftime('%H:%M'),
                'end_time': schedule.end_time.strftime('%H:%M'),
                'subject': schedule.subject or '',
                'room': schedule.room or '',
                'session': schedule.session
            })

        return jsonify({
            'success': True,
            'schedules': schedule_data,
            'count': len(schedule_data)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
