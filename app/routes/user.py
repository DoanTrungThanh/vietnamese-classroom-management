from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app import db
from app.models.user import User
from app.models.class_model import Class
from app.models.student import Student
from app.models.schedule import Schedule
from app.models.attendance import Attendance
from app.models.finance import Finance
from functools import wraps

bp = Blueprint('user', __name__, url_prefix='/user')

def user_required(f):
    """Decorator to require user role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not (current_user.is_user() or current_user.is_manager() or current_user.is_admin()):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@user_required
def dashboard():
    """User dashboard with limited statistics"""
    today = date.today()
    current_month = today.replace(day=1)
    
    # Basic statistics for user
    stats = {
        'total_classes': Class.query.filter_by(is_active=True).count(),
        'total_students': Student.query.count(),
        'today_schedules': 0,
        'this_month_attendance': 0
    }
    
    # Get today's schedules
    day_of_week = today.weekday() + 1
    if day_of_week == 7:  # Sunday
        day_of_week = 0
    
    today_schedules = Schedule.query.filter_by(
        day_of_week=day_of_week,
        is_active=True
    ).order_by(Schedule.session, Schedule.start_time).all()
    
    stats['today_schedules'] = len(today_schedules)
    
    # Get this month's attendance count
    next_month = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1)
    stats['this_month_attendance'] = Attendance.query.filter(
        Attendance.date >= current_month,
        Attendance.date < next_month
    ).count()
    
    return render_template('user/dashboard_tailwind.html',
                         title='Dashboard',
                         stats=stats,
                         today_schedules=today_schedules[:5])  # Limit to 5 schedules

@bp.route('/schedule/weekly')
@login_required
@user_required
def weekly_schedule():
    """View weekly schedule - read only"""
    from datetime import datetime, timedelta
    
    # Get week parameter
    week_str = request.args.get('week')
    if week_str:
        try:
            year, week = map(int, week_str.split('-W'))
            # Calculate first day of week
            jan1 = datetime(year, 1, 1)
            week_start = jan1 + timedelta(weeks=week-1, days=-jan1.weekday())
        except:
            week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    else:
        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    
    # Get schedules for the week
    schedules = Schedule.query.filter_by(is_active=True).order_by(
        Schedule.day_of_week, Schedule.session, Schedule.start_time
    ).all()
    
    # Group schedules by day
    week_schedules = {}
    for i in range(7):
        day_num = (i + 1) % 7  # Monday=1, Sunday=0
        week_schedules[i] = [s for s in schedules if s.day_of_week == day_num]
    
    return render_template('user/weekly_schedule_tailwind.html',
                         title='Lịch dạy tuần',
                         week_schedules=week_schedules,
                         week_start=week_start)

@bp.route('/schedule/monthly')
@login_required
@user_required
def monthly_schedule():
    """View monthly schedule - read only"""
    year = int(request.args.get('year', datetime.now().year))
    month = int(request.args.get('month', datetime.now().month))
    
    # Get all schedules for the month
    schedules = Schedule.query.filter_by(is_active=True).all()
    
    return render_template('user/monthly_schedule_tailwind.html',
                         title='Lịch dạy tháng',
                         schedules=schedules,
                         year=year,
                         month=month)

@bp.route('/finance/view')
@login_required
@user_required
def view_finance():
    """View finance records - read only"""
    page = request.args.get('page', 1, type=int)
    month = request.args.get('month')
    year = request.args.get('year')
    
    query = Finance.query
    
    # Filter by month/year if provided
    if month and year:
        try:
            start_date = datetime(int(year), int(month), 1)
            if int(month) == 12:
                end_date = datetime(int(year) + 1, 1, 1)
            else:
                end_date = datetime(int(year), int(month) + 1, 1)
            query = query.filter(Finance.date >= start_date, Finance.date < end_date)
        except ValueError:
            pass
    
    finances = query.order_by(Finance.date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Calculate totals
    total_income = db.session.query(db.func.sum(Finance.amount)).filter(
        Finance.type == 'income'
    ).scalar() or 0
    
    total_expense = db.session.query(db.func.sum(Finance.amount)).filter(
        Finance.type == 'expense'
    ).scalar() or 0
    
    return render_template('user/finance_view_tailwind.html',
                         title='Xem thu chi',
                         finances=finances,
                         total_income=total_income,
                         total_expense=total_expense)

@bp.route('/attendance/statistics')
@login_required
@user_required
def attendance_statistics():
    """View attendance statistics"""
    # Get date range
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    class_id = request.args.get('class_id')
    
    query = Attendance.query
    
    # Apply filters
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.date >= start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.date <= end)
        except ValueError:
            pass
    
    if class_id:
        try:
            query = query.join(Student).filter(Student.class_id == int(class_id))
        except ValueError:
            pass
    
    attendances = query.all()
    
    # Calculate statistics
    total_records = len(attendances)
    present_count = len([a for a in attendances if a.status == 'present'])
    absent_count = len([a for a in attendances if a.status == 'absent'])
    late_count = len([a for a in attendances if a.status == 'late'])
    
    # Daily statistics
    daily_stats = {}
    for attendance in attendances:
        date_str = attendance.date.strftime('%Y-%m-%d')
        if date_str not in daily_stats:
            daily_stats[date_str] = {'present': 0, 'absent': 0, 'late': 0, 'total': 0}
        daily_stats[date_str][attendance.status] += 1
        daily_stats[date_str]['total'] += 1
    
    # Get classes for filter
    classes = Class.query.filter_by(is_active=True).all()
    
    return render_template('user/attendance_statistics_tailwind.html',
                         title='Thống kê điểm danh',
                         total_records=total_records,
                         present_count=present_count,
                         absent_count=absent_count,
                         late_count=late_count,
                         daily_stats=daily_stats,
                         classes=classes,
                         start_date=start_date,
                         end_date=end_date,
                         selected_class_id=class_id)

@bp.route('/profile')
@login_required
@user_required
def profile():
    """User profile - read only"""
    return render_template('user/profile_tailwind.html',
                         title='Thông tin cá nhân',
                         user=current_user)
