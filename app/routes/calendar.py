from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app import db
from app.models.schedule import Schedule
from app.models.class_model import Class
from app.models.attendance import Attendance
from app.models.user import User

bp = Blueprint('calendar', __name__)

def get_week_dates(year, week):
    """Get start and end dates of a week"""
    jan1 = date(year, 1, 1)
    week_start = jan1 + timedelta(weeks=week-1)
    # Adjust to Monday
    week_start = week_start - timedelta(days=week_start.weekday())
    week_end = week_start + timedelta(days=6)
    return week_start, week_end

def get_current_week():
    """Get current week number and year"""
    today = date.today()
    year, week, _ = today.isocalendar()
    return year, week

@bp.route('/calendar')
@login_required
def calendar_view():
    """Main calendar view"""
    year = request.args.get('year', type=int)
    week = request.args.get('week', type=int)
    
    if not year or not week:
        year, week = get_current_week()
    
    week_start, week_end = get_week_dates(year, week)
    
    # Get schedules for the week based on user role
    # Filter schedules to only show those created in the selected week or current week
    from datetime import datetime, timedelta

    # Calculate the start and end of the selected week
    selected_week_start = week_start
    selected_week_end = week_end

    # Calculate current week for comparison
    today = date.today()
    current_week_start = today - timedelta(days=today.weekday())
    current_week_end = current_week_start + timedelta(days=6)

    # Get schedules for the specific week only
    selected_week_str = f"{year}-W{week:02d}"

    if current_user.is_admin():
        schedules = Schedule.query.filter_by(
            week_number=selected_week_str,
            is_active=True
        ).all()
    elif current_user.is_manager():
        managed_class_ids = [c.id for c in Class.query.filter_by(manager_id=current_user.id, is_active=True)]
        schedules = Schedule.query.filter(
            Schedule.class_id.in_(managed_class_ids),
            Schedule.week_number == selected_week_str,
            Schedule.is_active == True
        ).all()
    else:  # teacher
        schedules = Schedule.query.filter_by(
            teacher_id=current_user.id,
            week_number=selected_week_str,
            is_active=True
        ).all()
    
    # Create calendar data structure
    calendar_data = {}
    for day in range(7):  # Monday to Sunday
        current_date = week_start + timedelta(days=day)
        day_of_week = day + 1  # 1=Monday, 7=Sunday
        
        calendar_data[day_of_week] = {
            'date': current_date,
            'date_str': current_date.strftime('%d/%m'),
            'is_today': current_date == date.today(),
            'periods': {}
        }
        
        # Add schedules for this day
        day_schedules = [s for s in schedules if s.day_of_week == day_of_week]
        for schedule in day_schedules:
            if schedule.session not in calendar_data[day_of_week]['periods']:
                calendar_data[day_of_week]['periods'][schedule.session] = []

            # Check if there's attendance for this date
            attendance_count = Attendance.query.filter_by(
                schedule_id=schedule.id,
                date=current_date
            ).count()

            calendar_data[day_of_week]['periods'][schedule.session].append({
                'schedule': schedule,
                'has_attendance': attendance_count > 0,
                'attendance_count': attendance_count,
                'date': current_date
            })
    
    # Navigation data
    prev_week = week - 1 if week > 1 else 52
    prev_year = year if week > 1 else year - 1
    next_week = week + 1 if week < 52 else 1
    next_year = year if week < 52 else year + 1
    
    return render_template('calendar/calendar_tailwind.html',
                         title='Lịch dạy',
                         calendar_data=calendar_data,
                         current_year=year,
                         current_week=week,
                         week_start=week_start,
                         week_end=week_end,
                         prev_year=prev_year,
                         prev_week=prev_week,
                         next_year=next_year,
                         next_week=next_week,
                         timedelta=timedelta)

@bp.route('/calendar/day/<date_str>')
@login_required
def day_view(date_str):
    """Detailed view for a specific day"""
    try:
        view_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Ngày không hợp lệ', 'error')
        return redirect(url_for('calendar.calendar_view'))
    
    day_of_week = view_date.weekday() + 1  # Convert to 1=Monday format

    # Get week number for the specific date
    year, week, _ = view_date.isocalendar()
    week_str = f"{year}-W{week:02d}"

    # Get schedules for this day and week based on user role
    if current_user.is_admin():
        schedules = Schedule.query.filter_by(
            day_of_week=day_of_week,
            week_number=week_str,
            is_active=True
        ).order_by(Schedule.session, Schedule.start_time).all()
    elif current_user.is_manager():
        managed_class_ids = [c.id for c in Class.query.filter_by(manager_id=current_user.id, is_active=True)]
        schedules = Schedule.query.filter(
            Schedule.class_id.in_(managed_class_ids),
            Schedule.day_of_week == day_of_week,
            Schedule.week_number == week_str,
            Schedule.is_active == True
        ).order_by(Schedule.session, Schedule.start_time).all()
    else:  # teacher
        schedules = Schedule.query.filter_by(
            teacher_id=current_user.id,
            day_of_week=day_of_week,
            week_number=week_str,
            is_active=True
        ).order_by(Schedule.session, Schedule.start_time).all()
    
    # Get attendance data for each schedule
    schedule_data = []
    for schedule in schedules:
        attendance_records = Attendance.query.filter_by(
            schedule_id=schedule.id,
            date=view_date
        ).all()
        
        attendance_summary = {
            'total': schedule.class_obj.student_count,
            'present': len([a for a in attendance_records if a.status == 'present']),
            'absent_with_reason': len([a for a in attendance_records if a.status == 'absent_with_reason']),
            'absent_without_reason': len([a for a in attendance_records if a.status == 'absent_without_reason']),
            'not_taken': schedule.class_obj.student_count - len(attendance_records)
        }
        
        schedule_data.append({
            'schedule': schedule,
            'attendance_summary': attendance_summary,
            'attendance_records': attendance_records,
            'can_take_attendance': current_user.is_teacher() and schedule.teacher_id == current_user.id
        })
    
    return render_template('calendar/day_view_tailwind.html',
                         title=f'Lịch dạy {view_date.strftime("%d/%m/%Y")}',
                         view_date=view_date,
                         schedule_data=schedule_data,
                         timedelta=timedelta,
                         day_name=['', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật'][day_of_week])

@bp.route('/schedule/<int:schedule_id>/detail')
@login_required
def schedule_detail(schedule_id):
    """Get schedule details for modal"""
    schedule = Schedule.query.get_or_404(schedule_id)

    # Check permissions
    if current_user.is_teacher() and schedule.teacher_id != current_user.id:
        abort(403)
    elif current_user.is_manager() and schedule.class_obj.manager_id != current_user.id:
        abort(403)

    # Get attendance data for this schedule
    date_str = request.args.get('date')
    attendance_records = []
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            attendance_records = Attendance.query.filter_by(
                schedule_id=schedule_id,
                date=date_obj
            ).all()
        except ValueError:
            pass

    return render_template('calendar/schedule_detail_modal_tailwind.html',
                         schedule=schedule,
                         attendance_records=attendance_records,
                         date=date_str)

@bp.route('/calendar/month')
@login_required
def month_view():
    """Monthly calendar view"""
    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)

    # Validate year and month
    if year < 2020 or year > 2030:
        year = date.today().year
    if month < 1 or month > 12:
        month = date.today().month
    
    # Get first day of month and calculate calendar grid
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    # Calculate calendar grid (6 weeks)
    calendar_start = first_day - timedelta(days=first_day.weekday())
    calendar_end = calendar_start + timedelta(days=41)  # 6 weeks
    
    # Get all schedules for the month - collect all weeks in the month view
    week_numbers = []
    current_date = calendar_start
    while current_date <= calendar_end:
        year, week, _ = current_date.isocalendar()
        week_str = f"{year}-W{week:02d}"
        if week_str not in week_numbers:
            week_numbers.append(week_str)
        current_date += timedelta(days=7)

    if current_user.is_admin():
        schedules = Schedule.query.filter(
            Schedule.week_number.in_(week_numbers),
            Schedule.is_active == True
        ).all()
    elif current_user.is_manager():
        managed_class_ids = [c.id for c in Class.query.filter_by(manager_id=current_user.id, is_active=True)]
        schedules = Schedule.query.filter(
            Schedule.class_id.in_(managed_class_ids),
            Schedule.week_number.in_(week_numbers),
            Schedule.is_active == True
        ).all()
    else:  # teacher
        schedules = Schedule.query.filter(
            Schedule.teacher_id == current_user.id,
            Schedule.week_number.in_(week_numbers),
            Schedule.is_active == True
        ).all()
    
    # Build calendar data
    calendar_weeks = []
    current_date = calendar_start
    
    for week in range(6):
        week_data = []
        for day in range(7):
            day_of_week = day + 1  # 1=Monday

            # Get week number for this specific date
            year_iso, week_iso, _ = current_date.isocalendar()
            date_week_str = f"{year_iso}-W{week_iso:02d}"

            # Filter schedules by both day_of_week AND week_number
            day_schedules = [s for s in schedules
                           if s.day_of_week == day_of_week and s.week_number == date_week_str]

            week_data.append({
                'date': current_date,
                'is_current_month': current_date.month == month,
                'is_today': current_date == date.today(),
                'schedule_count': len(day_schedules),
                'schedules': day_schedules[:3],  # Show max 3 schedules
                'week_number': date_week_str
            })
            current_date += timedelta(days=1)

        calendar_weeks.append(week_data)
    
    # Navigation
    if month > 1:
        prev_month = date(year, month - 1, 1)
    else:
        prev_month = date(year - 1, 12, 1)

    if month < 12:
        next_month = date(year, month + 1, 1)
    else:
        next_month = date(year + 1, 1, 1)
    
    month_names = ['', 'Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6',
                   'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12']
    
    # Calculate statistics
    total_schedules = sum(len(day.get('schedules', [])) for week in calendar_weeks for day in week)
    working_days = sum(1 for week in calendar_weeks for day in week if day.get('schedules'))
    total_classes = len(set(schedule.class_id for week in calendar_weeks for day in week for schedule in day.get('schedules', [])))

    return render_template('calendar/month_view_tailwind.html',
                         title=f'Lịch tháng {month}/{year}',
                         calendar_weeks=calendar_weeks,
                         current_year=year,
                         current_month=month,
                         month_name=month_names[month],
                         prev_month=prev_month,
                         next_month=next_month,
                         total_schedules=total_schedules,
                         working_days=working_days,
                         total_classes=total_classes)
