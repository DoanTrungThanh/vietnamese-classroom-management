from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from app import db
from app.models.schedule import Schedule
from app.models.attendance import Attendance
from app.models.student import Student
from app.forms.schedule_forms import AttendanceForm

bp = Blueprint('teacher', __name__)

def teacher_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_teacher():
            flash('Bạn không có quyền truy cập trang này', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/schedule')
@login_required
@teacher_required
def schedule():
    schedules = Schedule.query.filter_by(teacher_id=current_user.id, is_active=True).all()
    # Group schedules by day and session for table display
    schedule_table = {}
    for schedule in schedules:
        if schedule.day_of_week not in schedule_table:
            schedule_table[schedule.day_of_week] = {}
        if schedule.session not in schedule_table[schedule.day_of_week]:
            schedule_table[schedule.day_of_week][schedule.session] = []
        schedule_table[schedule.day_of_week][schedule.session].append(schedule)
    
    return render_template('teacher/schedule.html', title='Lịch dạy của tôi', schedule_table=schedule_table)

@bp.route('/attendance/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def attendance(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    if schedule.teacher_id != current_user.id:
        flash('Bạn không có quyền truy cập tiết học này', 'error')
        return redirect(url_for('teacher.schedule'))
    
    # Get students enrolled in this specific schedule
    from app.models.student_schedule import StudentSchedule
    enrolled_student_ids = db.session.query(StudentSchedule.student_id).filter_by(
        schedule_id=schedule_id,
        is_active=True
    ).subquery()

    students = Student.query.filter(
        Student.id.in_(enrolled_student_ids),
        Student.is_active == True
    ).all()
    today = date.today()

    if request.method == 'POST':
        # Handle attendance submission
        try:
            # Delete existing attendance for this date
            Attendance.query.filter_by(
                schedule_id=schedule_id,
                date=today
            ).delete()

            # Save new attendance records
            for student in students:
                status = request.form.get(f'attendance_{student.id}')
                notes = request.form.get(f'notes_{student.id}', '')

                if status:
                    attendance = Attendance(
                        student_id=student.id,
                        schedule_id=schedule_id,
                        date=today,
                        status=status,
                        notes=notes
                    )
                    db.session.add(attendance)

            db.session.commit()
            flash('Điểm danh đã được lưu thành công', 'success')
            return redirect(url_for('teacher.attendance', schedule_id=schedule_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    # GET request - show attendance form
    # Get existing attendance records for today
    existing_attendance = {}
    for attendance_record in Attendance.query.filter_by(schedule_id=schedule_id, date=today).all():
        existing_attendance[attendance_record.student_id] = attendance_record

    from app.forms.schedule_forms import AttendanceForm
    form = AttendanceForm()  # Create form for CSRF token

    return render_template('teacher/attendance_tailwind.html',
                         title='Điểm danh',
                         schedule=schedule,
                         students=students,
                         existing_attendance=existing_attendance,
                         today=today,
                         form=form)


