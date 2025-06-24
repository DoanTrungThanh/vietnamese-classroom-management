from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
import random
import string
from app import db
from app.models.user import User
from app.models.class_model import Class
from app.models.student import Student
from app.models.schedule import Schedule
from app.models.attendance import Attendance
from app.models.event import Event
from app.models.finance import Finance
from app.models.time_slot import TimeSlot
from datetime import time, datetime
import json
from app.forms.class_forms import ClassForm, StudentForm
from app.forms.schedule_forms import ScheduleForm
from app.forms.event_forms import EventForm
from app.forms.finance_forms import FinanceForm
from app.forms.time_slot_forms import TimeSlotForm

bp = Blueprint('manager', __name__)

def generate_student_code():
    """Generate unique student code using hash starting from 1000"""
    import hashlib
    from datetime import datetime

    # Start from 1000 and find next available number
    base_number = 1000

    while True:
        # Check if this number already exists as student code
        student_code = str(base_number)
        existing = Student.query.filter_by(student_code=student_code).first()

        if not existing:
            # Found available number, optionally add hash for extra uniqueness
            timestamp = str(datetime.now().timestamp())
            hash_input = f"{base_number}{timestamp}"
            hash_object = hashlib.md5(hash_input.encode())
            hash_suffix = hash_object.hexdigest()[:2].upper()

            # For simplicity, just return the base number
            # You can uncomment below line to add hash suffix: 1000AB, 1001CD, etc.
            # student_code = f"{base_number}{hash_suffix}"

            return student_code

        # If exists, try next number
        base_number += 1

        # Safety check to prevent infinite loop
        if base_number > 9999:
            # Fallback to timestamp-based code if we run out of 4-digit numbers
            timestamp = str(int(datetime.now().timestamp()))[-4:]
            return f"HS{timestamp}"

def manager_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_admin() or current_user.is_manager()):
            flash('Bạn không có quyền truy cập trang này', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/classes')
@login_required
@manager_required
def classes():
    if current_user.is_admin():
        classes = Class.query.filter_by(is_active=True).all()
    else:
        classes = Class.query.filter_by(manager_id=current_user.id, is_active=True).all()
    return render_template('manager/classes_tailwind.html', title='Quản lý lớp học', classes=classes)

@bp.route('/class/<int:class_id>/details')
@login_required
@manager_required
def class_details(class_id):
    """Get class details for modal"""
    class_obj = Class.query.get_or_404(class_id)

    # Check permissions
    if not current_user.is_admin() and class_obj.manager_id != current_user.id:
        abort(403)

    # Get schedules for this class
    schedules = Schedule.query.filter_by(class_id=class_id, is_active=True).all()

    # Get students count
    students_count = Student.query.filter_by(class_id=class_id, is_active=True).count()

    return render_template('manager/class_details_modal_tailwind.html',
                         class_obj=class_obj,
                         schedules=schedules,
                         students_count=students_count)

@bp.route('/students')
@login_required
@manager_required
def students():
    page = request.args.get('page', 1, type=int)
    if current_user.is_admin():
        students = Student.query.filter_by(is_active=True).paginate(
            page=page, per_page=20, error_out=False)
    else:
        # Show all active students for manager (including those without class)
        # Manager can assign students to their classes later
        students = Student.query.filter_by(is_active=True).paginate(
            page=page, per_page=20, error_out=False)

    # Get unique class names for filter
    class_names = []
    return render_template('manager/students_tailwind.html', title='Quản lý học sinh',
                         students=students, class_names=class_names)

@bp.route('/students/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_student():
    from app.forms.user_forms import CreateStudentForm
    from datetime import datetime
    form = CreateStudentForm()

    # No need to set class choices since students don't belong to specific classes
    # Students will be assigned to classes through schedule assignments

    if form.validate_on_submit():
        # Generate unique student code
        student_code = generate_student_code()

        try:
            student = Student(
                student_code=student_code,
                full_name=form.full_name.data,
                date_of_birth=form.date_of_birth.data,
                address=form.address.data,
                parent_name=form.parent_name.data,
                parent_phone=form.parent_phone.data,
                profile_url=form.profile_url.data,
                class_id=None,  # Students don't belong to specific classes initially
                is_active=form.is_active.data,
                created_at=datetime.utcnow()
            )
            db.session.add(student)
            db.session.commit()
            flash('Thêm học sinh thành công! Học sinh sẽ được phân vào lớp thông qua lịch dạy.', 'success')
            return redirect(url_for('manager.students'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
            return render_template('manager/create_student_tailwind.html', title='Thêm học sinh', form=form)
    return render_template('manager/create_student_tailwind.html', title='Thêm học sinh', form=form)

@bp.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_student(student_id):
    from app.forms.user_forms import EditStudentForm
    student = Student.query.get_or_404(student_id)

    # Check permissions
    if not current_user.is_admin():
        if not student.class_obj or student.class_obj.manager_id != current_user.id:
            flash('Bạn không có quyền chỉnh sửa học sinh này', 'error')
            return redirect(url_for('manager.students'))

    form = EditStudentForm()

    # Filter classes based on user role
    if current_user.is_admin():
        classes = Class.query.filter_by(is_active=True).all()
        form.class_id.choices = [(0, 'Chọn lớp học')] + [(c.id, c.name) for c in classes]
    else:
        managed_classes = Class.query.filter_by(manager_id=current_user.id, is_active=True).all()
        form.class_id.choices = [(0, 'Chọn lớp học')] + [(c.id, c.name) for c in managed_classes]

    if form.validate_on_submit():
        # Check for duplicate student code (excluding current student)
        existing_student = Student.query.filter(
            Student.student_code == form.student_code.data,
            Student.id != student_id
        ).first()
        if existing_student:
            flash('Mã học sinh đã tồn tại', 'error')
            return render_template('manager/edit_student_tailwind.html', title='Chỉnh sửa học sinh', form=form, student=student)

        student.student_code = form.student_code.data
        student.full_name = form.full_name.data
        student.date_of_birth = form.date_of_birth.data
        student.address = form.address.data
        student.parent_name = form.parent_name.data
        student.parent_phone = form.parent_phone.data
        student.profile_url = form.profile_url.data
        student.class_id = form.class_id.data

        db.session.commit()
        flash('Cập nhật học sinh thành công!', 'success')
        return redirect(url_for('manager.students'))

    # Pre-populate form with student data
    if request.method == 'GET':
        form.student_code.data = student.student_code
        form.full_name.data = student.full_name
        form.date_of_birth.data = student.date_of_birth
        form.address.data = student.address
        form.parent_name.data = student.parent_name
        form.parent_phone.data = student.parent_phone
        form.profile_url.data = student.profile_url
        form.class_id.data = student.class_id
        form.is_active.data = student.is_active

    return render_template('manager/edit_student_tailwind.html', title='Chỉnh sửa học sinh', form=form, student=student)

@bp.route('/students/<int:student_id>/delete', methods=['POST'])
@login_required
@manager_required
def delete_student(student_id):
    """Delete student - Remove from all classes and schedules"""
    student = Student.query.get_or_404(student_id)

    # Check permissions
    if not current_user.is_admin():
        if not student.class_obj or student.class_obj.manager_id != current_user.id:
            flash('Bạn không có quyền xóa học sinh này', 'error')
            return redirect(url_for('manager.students'))

    try:
        # Get enrollment and attendance info for message
        from app.models.student_schedule import StudentSchedule
        from app.models.attendance import Attendance

        enrollments = StudentSchedule.query.filter_by(
            student_id=student_id,
            is_active=True
        ).count()

        attendance_records = Attendance.query.filter_by(student_id=student_id).count()

        # Remove student from all schedule enrollments
        StudentSchedule.query.filter_by(
            student_id=student_id,
            is_active=True
        ).update({'is_active': False})

        # Remove student from class
        student.class_id = None

        # Soft delete student
        student.is_active = False
        db.session.commit()

        # Create informative message
        message = f'Xóa học sinh {student.full_name} thành công'
        if enrollments > 0:
            message += f' (đã hủy đăng ký {enrollments} lịch học)'
        if attendance_records > 0:
            message += f' (có {attendance_records} bản ghi điểm danh)'

        flash(message, 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    return redirect(url_for('manager.students'))

@bp.route('/schedule')
@login_required
@manager_required
def schedule():
    if current_user.is_admin():
        schedules = Schedule.query.filter_by(is_active=True).all()
        classes = Class.query.filter_by(is_active=True).all()
    else:
        managed_class_ids = [c.id for c in Class.query.filter_by(manager_id=current_user.id, is_active=True)]
        schedules = Schedule.query.filter(Schedule.class_id.in_(managed_class_ids),
                                        Schedule.is_active==True).all()
        classes = Class.query.filter_by(manager_id=current_user.id, is_active=True).all()

    # Group schedules by day and session for table display
    schedule_table = {}
    for schedule in schedules:
        if schedule.day_of_week not in schedule_table:
            schedule_table[schedule.day_of_week] = {}
        if schedule.session not in schedule_table[schedule.day_of_week]:
            schedule_table[schedule.day_of_week][schedule.session] = []
        schedule_table[schedule.day_of_week][schedule.session].append(schedule)

    # Get additional data for the new template
    schedules = Schedule.query.filter_by(is_active=True).all()
    teachers = User.query.filter_by(role='teacher', is_active=True).all()
    time_slots = TimeSlot.query.filter_by(is_active=True).all()

    return render_template('manager/schedule_tailwind.html', title='Lịch dạy',
                         schedules=schedules, classes=classes, teachers=teachers, time_slots=time_slots)

@bp.route('/schedule/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_schedule():
    from app.forms.schedule_forms import ScheduleForm
    from datetime import datetime

    form = ScheduleForm()

    # Filter classes based on user role
    if not current_user.is_admin():
        managed_classes = Class.query.filter_by(manager_id=current_user.id, is_active=True).all()
        form.class_id.choices = [(c.id, c.name) for c in managed_classes]

    if form.validate_on_submit():
        try:
            # Validate permissions
            if not current_user.is_admin():
                class_obj = Class.query.get(form.class_id.data)
                if not class_obj or class_obj.manager_id != current_user.id:
                    flash('Bạn không có quyền tạo lịch cho lớp này', 'error')
                    return redirect(url_for('manager.schedule'))

            # Validate time logic
            if form.start_time.data >= form.end_time.data:
                flash('Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc', 'error')
                return render_template('manager/schedule_form_tailwind.html', form=form, title='Tạo lịch dạy')

            # Check for teacher conflicts in the same week
            teacher_conflict = Schedule.query.filter_by(
                day_of_week=form.day_of_week.data,
                teacher_id=form.teacher_id.data,
                week_number=form.week_number.data,
                is_active=True
            ).filter(
                Schedule.start_time < form.end_time.data,
                Schedule.end_time > form.start_time.data
            ).first()

            if teacher_conflict:
                flash('Giáo viên đã có lịch dạy trùng thời gian này trong tuần được chọn', 'error')
                return render_template('manager/schedule_form_tailwind.html', form=form, title='Tạo lịch dạy')

            # Check for class conflicts in the same week
            class_conflict = Schedule.query.filter_by(
                day_of_week=form.day_of_week.data,
                class_id=form.class_id.data,
                week_number=form.week_number.data,
                is_active=True
            ).filter(
                Schedule.start_time < form.end_time.data,
                Schedule.end_time > form.start_time.data
            ).first()

            if class_conflict:
                flash('Lớp học đã có lịch dạy trùng thời gian này trong tuần được chọn', 'error')
                return render_template('manager/schedule_form_tailwind.html', form=form, title='Tạo lịch dạy')

            # Create new schedule
            current_week = Schedule.get_current_week()
            schedule = Schedule(
                class_id=form.class_id.data,
                teacher_id=form.teacher_id.data,
                day_of_week=form.day_of_week.data,
                session=form.session.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                subject=form.subject.data or '',
                room=form.room.data or '',
                week_number=form.week_number.data,
                week_created=current_week,
                is_active=True,
                created_at=datetime.utcnow()
            )

            db.session.add(schedule)
            db.session.flush()  # Get schedule ID

            # Auto-enroll all students in this class to the new schedule
            students_in_class = Student.query.filter_by(class_id=form.class_id.data, is_active=True).all()
            enrolled_count = 0

            if students_in_class:
                from app.models.student_schedule import StudentSchedule
                for student in students_in_class:
                    # Check if already enrolled (shouldn't happen for new schedule, but safety check)
                    existing = StudentSchedule.query.filter_by(
                        student_id=student.id,
                        schedule_id=schedule.id,
                        is_active=True
                    ).first()

                    if not existing:
                        enrollment = StudentSchedule(
                            student_id=student.id,
                            schedule_id=schedule.id,
                            is_active=True
                        )
                        db.session.add(enrollment)
                        enrolled_count += 1

            db.session.commit()

            # Create success message with enrollment info
            if enrolled_count > 0:
                flash(f'Tạo lịch dạy thành công! Đã tự động đăng ký {enrolled_count} học sinh vào lịch.', 'success')
            else:
                flash('Tạo lịch dạy thành công! Lớp chưa có học sinh, hãy thêm học sinh vào lớp.', 'success')

            return redirect(url_for('manager.schedule'))

        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
            return render_template('manager/schedule_form_tailwind.html', form=form, title='Tạo lịch dạy')

    return render_template('manager/schedule_form_tailwind.html', form=form, title='Tạo lịch dạy')

@bp.route('/schedule/copy', methods=['GET', 'POST'])
@login_required
@manager_required
def copy_schedule():
    """Copy schedules from one week to another"""
    from app.forms.schedule_forms import CopyScheduleForm
    from app.models.student_schedule import StudentSchedule

    form = CopyScheduleForm()

    if form.validate_on_submit():
        try:
            source_week = form.source_week.data
            target_week = form.target_week.data
            copy_type = form.copy_all.data
            class_id = form.class_id.data if form.class_id.data != 0 else None

            # Build query for source schedules
            query = Schedule.query.filter_by(
                week_number=source_week,
                is_active=True
            )

            # Filter by class if specified
            if copy_type == 'class' and class_id:
                query = query.filter_by(class_id=class_id)

                # Check permissions for specific class
                if not current_user.is_admin():
                    class_obj = Class.query.get(class_id)
                    if not class_obj or class_obj.manager_id != current_user.id:
                        flash('Bạn không có quyền sao chép lịch của lớp này', 'error')
                        return render_template('manager/copy_schedule_new_tailwind.html', form=form, title='Sao chép lịch dạy')

            source_schedules = query.all()

            if not source_schedules:
                flash('Không tìm thấy lịch dạy nào trong tuần nguồn', 'warning')
                return render_template('manager/copy_schedule_new_tailwind.html', form=form, title='Sao chép lịch dạy')

            # Check for existing schedules in target week (only for user's classes)
            if not current_user.is_admin():
                managed_class_ids = [c.id for c in Class.query.filter_by(manager_id=current_user.id, is_active=True)]
                existing_count = Schedule.query.filter(
                    Schedule.week_number == target_week,
                    Schedule.class_id.in_(managed_class_ids),
                    Schedule.is_active == True
                ).count()
            else:
                existing_count = Schedule.query.filter_by(
                    week_number=target_week,
                    is_active=True
                ).count()

            if existing_count > 0:
                flash(f'Tuần đích đã có {existing_count} lịch dạy. Bạn có muốn tiếp tục sao chép không?', 'warning')

            # Copy schedules
            copied_count = 0
            current_week = Schedule.get_current_week()

            for source_schedule in source_schedules:
                # Check permissions for each schedule
                if not current_user.is_admin():
                    if source_schedule.class_obj.manager_id != current_user.id:
                        continue  # Skip schedules user doesn't manage

                # Create new schedule
                new_schedule = Schedule(
                    class_id=source_schedule.class_id,
                    teacher_id=source_schedule.teacher_id,
                    day_of_week=source_schedule.day_of_week,
                    session=source_schedule.session,
                    start_time=source_schedule.start_time,
                    end_time=source_schedule.end_time,
                    subject=source_schedule.subject,
                    room=source_schedule.room,
                    week_number=target_week,
                    week_created=current_week,
                    is_active=True,
                    created_at=datetime.utcnow()
                )

                db.session.add(new_schedule)
                db.session.flush()  # Get new schedule ID

                # Copy student enrollments
                source_enrollments = StudentSchedule.query.filter_by(
                    schedule_id=source_schedule.id,
                    is_active=True
                ).all()

                for enrollment in source_enrollments:
                    new_enrollment = StudentSchedule(
                        student_id=enrollment.student_id,
                        schedule_id=new_schedule.id,
                        is_active=True
                    )
                    db.session.add(new_enrollment)

                copied_count += 1

            db.session.commit()

            if copied_count > 0:
                flash(f'Đã sao chép {copied_count} lịch dạy từ {source_week} sang {target_week}', 'success')
            else:
                flash('Không có lịch dạy nào được sao chép (có thể do quyền hạn)', 'warning')

            return redirect(url_for('manager.schedule'))

        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    return render_template('manager/copy_schedule_new_tailwind.html', form=form, title='Sao chép lịch dạy')

@bp.route('/schedule/<int:schedule_id>/add_students', methods=['GET', 'POST'])
@login_required
@manager_required
def add_students_to_schedule(schedule_id):
    """Add students to a specific schedule"""
    from app.models.student_schedule import StudentSchedule

    schedule = Schedule.query.get_or_404(schedule_id)

    # Check permissions
    if not current_user.is_admin() and schedule.class_obj.manager_id != current_user.id:
        flash('Bạn không có quyền thêm học sinh vào lịch này', 'error')
        return redirect(url_for('manager.schedule'))

    if request.method == 'GET':
        # Get students not enrolled in this schedule
        enrolled_student_ids = [ss.student_id for ss in schedule.student_enrollments if ss.is_active]
        available_students = Student.query.filter(
            ~Student.id.in_(enrolled_student_ids),
            Student.is_active == True
        ).all()

        return render_template('manager/add_students_to_schedule_tailwind.html',
                             title=f'Thêm học sinh vào lịch {schedule.class_obj.name}',
                             schedule=schedule,
                             available_students=available_students)

    elif request.method == 'POST':
        student_ids = request.form.getlist('student_ids')
        if not student_ids:
            flash('Vui lòng chọn ít nhất một học sinh', 'error')
            return redirect(url_for('manager.add_students_to_schedule', schedule_id=schedule_id))

        try:
            added_count = 0
            for student_id in student_ids:
                student = Student.query.get(student_id)
                if student and student.is_active:
                    # Check if already enrolled
                    existing = StudentSchedule.query.filter_by(
                        student_id=student_id,
                        schedule_id=schedule_id,
                        is_active=True
                    ).first()

                    if not existing:
                        enrollment = StudentSchedule(
                            student_id=student_id,
                            schedule_id=schedule_id,
                            is_active=True
                        )
                        db.session.add(enrollment)
                        added_count += 1

            db.session.commit()
            flash(f'Đã thêm {added_count} học sinh vào lịch dạy', 'success')
            return redirect(url_for('manager.schedule'))

        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
            return redirect(url_for('manager.add_students_to_schedule', schedule_id=schedule_id))

@bp.route('/class/<int:class_id>/add_student_no_csrf', methods=['GET', 'POST'])
@login_required
@manager_required
def add_student_to_class_no_csrf(class_id):
    """Add existing student to class - No CSRF version"""
    class_obj = Class.query.get_or_404(class_id)

    # Check permissions
    if not current_user.is_admin() and class_obj.manager_id != current_user.id:
        flash('Bạn không có quyền thêm học sinh vào lớp này', 'error')
        return redirect(url_for('manager.classes'))

    # Get all active students
    available_students = Student.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        # Manual form processing without CSRF
        student_ids = request.form.getlist('student_ids')

        if not student_ids:
            flash('Vui lòng chọn ít nhất một học sinh', 'error')
        else:
            try:
                # Get all schedules for this class
                schedules = Schedule.query.filter_by(class_id=class_id, is_active=True).all()

                if not schedules:
                    flash('Lớp này chưa có lịch dạy. Vui lòng tạo lịch dạy trước.', 'warning')
                    return redirect(url_for('manager.schedule'))

                added_count = 0
                for student_id in student_ids:
                    student = Student.query.get(int(student_id))
                    if student and student.is_active:
                        # Add student to all schedules of this class
                        for schedule in schedules:
                            # Check if already enrolled
                            from app.models.student_schedule import StudentSchedule
                            existing = StudentSchedule.query.filter_by(
                                student_id=student_id,
                                schedule_id=schedule.id,
                                is_active=True
                            ).first()

                            if not existing:
                                enrollment = StudentSchedule(
                                    student_id=student_id,
                                    schedule_id=schedule.id,
                                    is_active=True
                                )
                                db.session.add(enrollment)
                        added_count += 1

                db.session.commit()
                flash(f'Đã thêm {added_count} học sinh vào tất cả lịch dạy của lớp {class_obj.name}', 'success')
                return redirect(url_for('manager.classes'))

            except Exception as e:
                db.session.rollback()
                flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    return render_template('manager/add_student_to_class_no_csrf_tailwind.html',
                         title=f'Thêm học sinh vào {class_obj.name}',
                         class_obj=class_obj,
                         available_students=available_students)

@bp.route('/class/<int:class_id>/add_student', methods=['GET', 'POST'])
@login_required
@manager_required
def add_student_to_class(class_id):
    """Add existing student to class - CSRF exempt version"""
    class_obj = Class.query.get_or_404(class_id)

    # Check permissions
    if not current_user.is_admin() and class_obj.manager_id != current_user.id:
        flash('Bạn không có quyền thêm học sinh vào lớp này', 'error')
        return redirect(url_for('manager.classes'))

    # Get all active students
    available_students = Student.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        # Manual form processing
        student_ids = request.form.getlist('student_ids')

        if not student_ids:
            flash('Vui lòng chọn ít nhất một học sinh', 'error')
        else:
            try:
                added_count = 0
                for student_id in student_ids:
                    student = Student.query.get(int(student_id))
                    if student and student.is_active:
                        # Assign student to class
                        student.class_id = class_id
                        added_count += 1

                        # If there are existing schedules, enroll student automatically
                        schedules = Schedule.query.filter_by(class_id=class_id, is_active=True).all()
                        if schedules:
                            for schedule in schedules:
                                # Check if already enrolled
                                from app.models.student_schedule import StudentSchedule
                                existing = StudentSchedule.query.filter_by(
                                    student_id=student_id,
                                    schedule_id=schedule.id,
                                    is_active=True
                                ).first()

                                if not existing:
                                    enrollment = StudentSchedule(
                                        student_id=student_id,
                                        schedule_id=schedule.id,
                                        is_active=True
                                    )
                                    db.session.add(enrollment)

                db.session.commit()

                # Create appropriate success message
                schedules_count = Schedule.query.filter_by(class_id=class_id, is_active=True).count()
                if schedules_count > 0:
                    flash(f'Đã thêm {added_count} học sinh vào lớp {class_obj.name} và tự động đăng ký vào {schedules_count} lịch dạy', 'success')
                else:
                    flash(f'Đã thêm {added_count} học sinh vào lớp {class_obj.name}. Tạo lịch dạy để học sinh có thể học.', 'success')

                return redirect(url_for('manager.classes'))

            except Exception as e:
                db.session.rollback()
                flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    return render_template('manager/add_student_to_class_simple_tailwind.html',
                         title=f'Thêm học sinh vào {class_obj.name}',
                         class_obj=class_obj,
                         available_students=available_students)

@bp.route('/class/<int:class_id>/info')
@login_required
@manager_required
def class_info(class_id):
    """Show class details"""
    class_obj = Class.query.get_or_404(class_id)

    # Check permissions
    if not current_user.is_admin() and class_obj.manager_id != current_user.id:
        flash('Bạn không có quyền xem lớp này', 'error')
        return redirect(url_for('manager.classes'))

    return render_template('manager/class_details_tailwind.html',
                         title=f'Chi tiết lớp {class_obj.name}',
                         class_obj=class_obj)

@bp.route('/class/<int:class_id>/edit', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_class(class_id):
    """Edit class"""
    from app.forms.class_forms import ClassForm

    class_obj = Class.query.get_or_404(class_id)

    # Check permissions
    if not current_user.is_admin() and class_obj.manager_id != current_user.id:
        flash('Bạn không có quyền chỉnh sửa lớp này', 'error')
        return redirect(url_for('manager.classes'))

    form = ClassForm(obj=class_obj)

    # Filter managers based on user role
    if current_user.is_admin():
        managers = User.query.filter_by(role='manager', is_active=True).all()
        form.manager_id.choices = [(0, 'Chọn quản sinh')] + [(m.id, m.full_name) for m in managers]
    else:
        # Manager can only assign themselves
        form.manager_id.choices = [(current_user.id, current_user.full_name)]
        form.manager_id.data = current_user.id

    if form.validate_on_submit():
        try:
            # Check for duplicate class name (excluding current class)
            existing = Class.query.filter(
                Class.name == form.name.data,
                Class.id != class_id
            ).first()

            if existing:
                flash('Tên lớp đã tồn tại', 'error')
                return render_template('manager/edit_class_tailwind.html',
                                     title='Chỉnh sửa lớp học', form=form, class_obj=class_obj)

            # Update class data
            class_obj.name = form.name.data
            class_obj.description = form.description.data
            class_obj.manager_id = form.manager_id.data if form.manager_id.data != 0 else None
            class_obj.is_active = form.is_active.data

            db.session.commit()
            flash('Cập nhật lớp học thành công!', 'success')
            return redirect(url_for('manager.classes'))

        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    return render_template('manager/edit_class_tailwind.html',
                         title='Chỉnh sửa lớp học',
                         form=form,
                         class_obj=class_obj)

@bp.route('/class/<int:class_id>/delete', methods=['POST'])
@login_required
@manager_required
def delete_class(class_id):
    """Delete class - Allow deletion even with active students and schedules"""
    from flask import jsonify

    class_obj = Class.query.get_or_404(class_id)

    # Check permissions
    if not current_user.is_admin() and class_obj.manager_id != current_user.id:
        return jsonify({'success': False, 'message': 'Bạn không có quyền xóa lớp này'}), 403

    try:
        # Get counts for info message
        active_students = Student.query.filter_by(class_id=class_id, is_active=True).count()
        active_schedules = Schedule.query.filter_by(class_id=class_id, is_active=True).count()

        # Get attendance count
        from app.models.attendance import Attendance
        attendance_count = Attendance.query.join(Schedule).filter(
            Schedule.class_id == class_id,
            Schedule.is_active == True
        ).count()

        # Remove students from this class
        Student.query.filter_by(class_id=class_id, is_active=True).update({'class_id': None})

        # Deactivate all schedules for this class
        Schedule.query.filter_by(class_id=class_id, is_active=True).update({'is_active': False})

        # Deactivate all student enrollments for schedules in this class
        from app.models.student_schedule import StudentSchedule
        schedule_ids = [s.id for s in Schedule.query.filter_by(class_id=class_id).all()]
        if schedule_ids:
            StudentSchedule.query.filter(
                StudentSchedule.schedule_id.in_(schedule_ids),
                StudentSchedule.is_active == True
            ).update({'is_active': False}, synchronize_session=False)

        # Soft delete the class
        class_obj.is_active = False
        db.session.commit()

        # Create informative message
        message = f'Xóa lớp {class_obj.name} thành công'
        if active_students > 0:
            message += f' (đã chuyển {active_students} học sinh ra khỏi lớp)'
        if active_schedules > 0:
            message += f' (đã hủy {active_schedules} lịch dạy)'
        if attendance_count > 0:
            message += f' (có {attendance_count} bản ghi điểm danh)'

        return jsonify({'success': True, 'message': message})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'})

@bp.route('/api/time-slots/<session>')
def get_time_slots_by_session(session):
    """Get time slots by session for AJAX"""
    time_slots = []

    if session == 'morning':
        time_slots = [
            {'start': '07:30', 'end': '09:00'},
            {'start': '09:15', 'end': '10:45'},
            {'start': '11:00', 'end': '12:30'}
        ]
    elif session == 'afternoon':
        time_slots = [
            {'start': '13:30', 'end': '15:00'},
            {'start': '15:15', 'end': '16:45'},
            {'start': '17:00', 'end': '18:30'}
        ]
    elif session == 'evening':
        time_slots = [
            {'start': '18:30', 'end': '20:00'},
            {'start': '20:15', 'end': '21:45'}
        ]

    return jsonify(time_slots)

@bp.route('/class/<int:class_id>/teachers', methods=['GET', 'POST'])
@login_required
@manager_required
def class_teachers(class_id):
    from flask import jsonify

    class_obj = Class.query.get_or_404(class_id)

    # Check permissions
    if not current_user.is_admin() and class_obj.manager_id != current_user.id:
        return jsonify({'error': 'Không có quyền truy cập'}), 403

    if request.method == 'GET':
        # Return teachers for this class
        all_teachers = User.query.filter_by(role='teacher', is_active=True).all()
        assigned_teachers = class_obj.teachers

        return jsonify({
            'all_teachers': [{'id': t.id, 'full_name': t.full_name, 'phone': t.phone} for t in all_teachers],
            'assigned_teachers': [{'id': t.id, 'full_name': t.full_name} for t in assigned_teachers],
            'teachers': [{'id': t.id, 'full_name': t.full_name} for t in assigned_teachers]  # For schedule form
        })

    elif request.method == 'POST':
        # Update teachers for this class
        data = request.get_json()
        teacher_ids = data.get('teacher_ids', [])

        # Clear existing teachers
        class_obj.teachers.clear()

        # Add new teachers
        for teacher_id in teacher_ids:
            teacher = User.query.get(teacher_id)
            if teacher and teacher.role == 'teacher':
                class_obj.teachers.append(teacher)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Cập nhật giáo viên thành công'})

@bp.route('/manager/get_all_teachers')
@login_required
@manager_required
def get_all_teachers():
    """Get all active teachers for schedule assignment"""
    teachers = User.query.filter_by(role='teacher', is_active=True).all()
    teachers_data = [{'id': t.id, 'full_name': t.full_name} for t in teachers]
    return jsonify({'teachers': teachers_data})

@bp.route('/attendance')
@login_required
@manager_required
def attendance():
    """View attendance overview for manager"""
    from datetime import date, timedelta, datetime

    # Get date filter
    date_filter = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    try:
        filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
    except ValueError:
        filter_date = date.today()

    # Get class filter
    class_filter = request.args.get('class_id', type=int)

    # Get managed classes
    if current_user.is_admin():
        managed_classes = Class.query.filter_by(is_active=True).all()
    else:
        managed_classes = Class.query.filter_by(manager_id=current_user.id, is_active=True).all()

    managed_class_ids = [c.id for c in managed_classes]

    # Build attendance query
    attendance_query = Attendance.query.join(Schedule).join(Student).filter(
        Attendance.date == filter_date,
        Schedule.class_id.in_(managed_class_ids),
        Student.is_active == True
    )

    if class_filter:
        attendance_query = attendance_query.filter(Schedule.class_id == class_filter)

    attendances = attendance_query.order_by(Schedule.class_id, Student.full_name).all()

    # Group by class and schedule
    attendance_by_class = {}
    for attendance in attendances:
        class_name = attendance.schedule.class_obj.name
        if class_name not in attendance_by_class:
            attendance_by_class[class_name] = {}

        schedule_key = f"{attendance.schedule.subject or 'Chưa xác định'} - {attendance.schedule.time_range}"
        if schedule_key not in attendance_by_class[class_name]:
            attendance_by_class[class_name][schedule_key] = []

        attendance_by_class[class_name][schedule_key].append(attendance)

    # Calculate statistics
    total_students = len(attendances)
    present_count = len([a for a in attendances if a.status == 'present'])
    absent_count = len([a for a in attendances if a.status in ['absent_with_reason', 'absent_without_reason']])
    attendance_rate = round((present_count / total_students * 100) if total_students > 0 else 0, 1)

    stats = {
        'total_students': total_students,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_rate': attendance_rate
    }

    return render_template('manager/attendance_tailwind.html',
                         title='Báo cáo điểm danh',
                         attendance_by_class=attendance_by_class,
                         managed_classes=managed_classes,
                         filter_date=filter_date,
                         class_filter=class_filter,
                         stats=stats)

@bp.route('/student/<int:student_id>/details')
@login_required
@manager_required
def student_details(student_id):
    from flask import jsonify

    student = Student.query.get_or_404(student_id)

    # Check permissions
    if not current_user.is_admin():
        if not student.class_obj or student.class_obj.manager_id != current_user.id:
            return jsonify({'error': 'Không có quyền truy cập'}), 403

    # Get recent attendance
    recent_attendance = Attendance.query.filter_by(student_id=student_id)\
        .order_by(Attendance.date.desc()).limit(10).all()

    return jsonify({
        'student_code': student.student_code,
        'full_name': student.full_name,
        'date_of_birth': student.date_of_birth.strftime('%d/%m/%Y') if student.date_of_birth else None,
        'class_name': student.class_obj.name if student.class_obj else None,
        'address': student.address,
        'parent_name': student.parent_name,
        'parent_phone': student.parent_phone,
        'profile_url': student.profile_url,
        'attendance_rate': student.attendance_rate,
        'recent_attendance': [{
            'date': a.date.strftime('%d/%m/%Y'),
            'subject': a.schedule.subject if a.schedule else None,
            'status': a.status,
            'status_display': a.status_display,
            'reason': a.reason
        } for a in recent_attendance]
    })

@bp.route('/manager/time_slots')
@login_required
@manager_required
def time_slots():
    """Manage time slots"""
    time_slots = TimeSlot.query.filter_by(is_active=True).order_by(TimeSlot.session_type, TimeSlot.start_time).all()

    # Group by session type
    slots_by_session = {}
    for slot in time_slots:
        if slot.session_type not in slots_by_session:
            slots_by_session[slot.session_type] = []
        slots_by_session[slot.session_type].append(slot)

    return render_template('manager/time_slots_tailwind.html',
                         title='Quản lý khung giờ',
                         slots_by_session=slots_by_session,
                         time_slots=time_slots)

@bp.route('/schedule/assignments')
@login_required
@manager_required
def schedule_assignments():
    # Get all schedule assignments
    assignments = Schedule.query.filter_by(is_active=True).all()

    # Get statistics
    active_teachers = User.query.filter_by(role='teacher', is_active=True).count()
    assigned_classes = len(set(assignment.class_id for assignment in assignments))
    used_time_slots = len(set((assignment.start_time, assignment.end_time) for assignment in assignments))

    # Get data for dropdowns
    teachers = User.query.filter_by(role='teacher', is_active=True).all()
    classes = Class.query.filter_by(is_active=True).all()
    time_slots = TimeSlot.query.filter_by(is_active=True).all()

    return render_template('manager/schedule_assignment_tailwind.html',
                         title='Phân công lịch dạy',
                         assignments=assignments,
                         active_teachers=active_teachers,
                         assigned_classes=assigned_classes,
                         used_time_slots=used_time_slots,
                         teachers=teachers,
                         classes=classes,
                         time_slots=time_slots)

@bp.route('/schedule/assign', methods=['POST'])
@login_required
@manager_required
def assign_schedule():
    try:
        # Get data from JSON or form
        if request.is_json:
            data = request.get_json()
            teacher_id = data.get('teacher_id')
            class_id = data.get('class_id')
            session = data.get('session')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            day_of_week = data.get('day_of_week')
            subject = data.get('subject', '')
            room = data.get('room', '')
        else:
            teacher_id = request.form.get('teacher_id')
            class_id = request.form.get('class_id')
            session = request.form.get('session')
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')
            day_of_week = request.form.get('day_of_week')
            subject = request.form.get('subject', '')
            room = request.form.get('room', '')

        # Validate required fields
        if not all([teacher_id, class_id, start_time, end_time, day_of_week]):
            return jsonify({'success': False, 'message': 'Vui lòng điền đầy đủ thông tin bắt buộc'})

        # Parse time strings
        from datetime import datetime
        try:
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
        except ValueError:
            return jsonify({'success': False, 'message': 'Định dạng thời gian không hợp lệ (HH:MM)'})

        # Validate time logic
        if start_time_obj >= end_time_obj:
            return jsonify({'success': False, 'message': 'Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc'})

        # Check for conflicts
        existing = Schedule.query.filter_by(
            teacher_id=teacher_id,
            day_of_week=int(day_of_week),
            is_active=True
        ).filter(
            Schedule.start_time < end_time_obj,
            Schedule.end_time > start_time_obj
        ).first()

        if existing:
            return jsonify({'success': False, 'message': 'Giáo viên đã có lịch dạy trùng thời gian này'})

        # Create new assignment
        schedule = Schedule(
            teacher_id=int(teacher_id),
            class_id=int(class_id),
            start_time=start_time_obj,
            end_time=end_time_obj,
            session=session or 'morning',
            day_of_week=int(day_of_week),
            subject=subject,
            room=room,
            is_active=True,
            created_at=datetime.utcnow()
        )

        db.session.add(schedule)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Phân công lịch dạy thành công!'})

    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Dữ liệu không hợp lệ: {str(e)}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'})

@bp.route('/schedule/assignment/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_assignment(id):
    """Edit schedule assignment"""
    from app.forms.schedule_forms import ScheduleForm
    from datetime import datetime

    assignment = Schedule.query.get_or_404(id)

    # Check permissions
    if not current_user.is_admin() and assignment.class_obj.manager_id != current_user.id:
        flash('Bạn không có quyền chỉnh sửa phân công này', 'error')
        return redirect(url_for('manager.schedule_assignments'))

    form = ScheduleForm()

    # Filter classes based on user role
    if current_user.is_admin():
        classes = Class.query.filter_by(is_active=True).all()
        form.class_id.choices = [(c.id, c.name) for c in classes]
    else:
        managed_classes = Class.query.filter_by(manager_id=current_user.id, is_active=True).all()
        form.class_id.choices = [(c.id, c.name) for c in managed_classes]

    if request.method == 'GET':
        # Populate form with assignment data
        form.class_id.data = assignment.class_id
        form.teacher_id.data = assignment.teacher_id
        form.day_of_week.data = assignment.day_of_week
        form.session.data = assignment.session
        form.start_time.data = assignment.start_time
        form.end_time.data = assignment.end_time
        form.subject.data = assignment.subject
        form.room.data = assignment.room

        return render_template('manager/edit_assignment_tailwind.html',
                             title='Chỉnh sửa phân công',
                             form=form,
                             assignment=assignment)

    elif form.validate_on_submit():
        try:
            # Validate time logic
            if form.start_time.data >= form.end_time.data:
                flash('Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc', 'error')
                return render_template('manager/edit_assignment_tailwind.html',
                                     title='Chỉnh sửa phân công',
                                     form=form,
                                     assignment=assignment)

            # Check for conflicts (excluding current assignment)
            existing = Schedule.query.filter(
                Schedule.id != assignment.id,
                Schedule.day_of_week == form.day_of_week.data,
                Schedule.teacher_id == form.teacher_id.data,
                Schedule.is_active == True
            ).filter(
                Schedule.start_time < form.end_time.data,
                Schedule.end_time > form.start_time.data
            ).first()

            if existing:
                flash('Giáo viên đã có lịch dạy trùng thời gian này', 'error')
                return render_template('manager/edit_assignment_tailwind.html',
                                     title='Chỉnh sửa phân công',
                                     form=form,
                                     assignment=assignment)

            # Update assignment data
            assignment.class_id = form.class_id.data
            assignment.teacher_id = form.teacher_id.data
            assignment.day_of_week = form.day_of_week.data
            assignment.session = form.session.data
            assignment.start_time = form.start_time.data
            assignment.end_time = form.end_time.data
            assignment.subject = form.subject.data or ''
            assignment.room = form.room.data or ''

            db.session.commit()
            flash('Cập nhật phân công thành công!', 'success')
            return redirect(url_for('manager.schedule_assignments'))

        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
            return render_template('manager/edit_assignment_tailwind.html',
                                 title='Chỉnh sửa phân công',
                                 form=form,
                                 assignment=assignment)

    # If form validation fails
    return render_template('manager/edit_assignment_tailwind.html',
                         title='Chỉnh sửa phân công',
                         form=form,
                         assignment=assignment)

@bp.route('/schedule/assignment/<int:id>/toggle', methods=['POST'])
@login_required
@manager_required
def toggle_assignment(id):
    try:
        assignment = Schedule.query.get_or_404(id)
        assignment.is_active = not assignment.is_active
        db.session.commit()

        status = 'kích hoạt' if assignment.is_active else 'tạm dừng'
        return jsonify({'success': True, 'message': f'Đã {status} phân công'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'})

@bp.route('/schedule/assignment/<int:id>/delete', methods=['POST'])
@login_required
@manager_required
def delete_assignment(id):
    try:
        assignment = Schedule.query.get_or_404(id)
        db.session.delete(assignment)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Xóa phân công thành công'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'})

@bp.route('/class/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_class():
    from app.forms.user_forms import CreateClassForm
    from datetime import datetime
    form = CreateClassForm()

    if form.validate_on_submit():
        try:
            class_obj = Class(
                name=form.name.data,
                description=form.description.data,
                manager_id=form.manager_id.data if form.manager_id.data != 0 else None,
                is_active=form.is_active.data,
                created_at=datetime.utcnow()
            )

            db.session.add(class_obj)
            db.session.commit()
            flash(f'Tạo lớp học {class_obj.name} thành công!', 'success')
            return redirect(url_for('manager.classes'))

        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    return render_template('manager/create_class_tailwind.html', title='Thêm lớp học', form=form)



@bp.route('/schedule/preview')
@login_required
@manager_required
def preview_schedule():
    try:
        week = request.args.get('week')
        if not week:
            return jsonify({'success': False, 'message': 'Thiếu thông tin tuần'})

        # Get schedules for preview (simplified - just get all active schedules)
        schedules = Schedule.query.filter_by(is_active=True).limit(10).all()

        if not schedules:
            return jsonify({'success': False, 'message': 'Không có lịch dạy'})

        # Generate preview HTML
        html = '<div class="space-y-3">'
        for schedule in schedules:
            day_name = {
                0: 'Chủ nhật', 1: 'Thứ 2', 2: 'Thứ 3', 3: 'Thứ 4',
                4: 'Thứ 5', 5: 'Thứ 6', 6: 'Thứ 7'
            }.get(schedule.day_of_week, f'Thứ {schedule.day_of_week}')

            html += f'''
            <div class="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div>
                    <div class="font-medium text-gray-900">{schedule.teacher.full_name} - {schedule.class_obj.name}</div>
                    <div class="text-sm text-gray-500">{day_name} • {schedule.session_name}</div>
                </div>
                <div class="text-sm text-blue-600">
                    {schedule.start_time.strftime('%H:%M')} - {schedule.end_time.strftime('%H:%M')}
                </div>
            </div>
            '''

        html += '</div>'

        return jsonify({'success': True, 'html': html})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'})

@bp.route('/classes/export')
@login_required
@manager_required
def export_classes():
    try:
        from app.utils.excel_export import export_classes_to_excel
        classes = Class.query.all()
        response = export_classes_to_excel(classes)
        if response:
            return response
        else:
            flash('Có lỗi xảy ra khi xuất file Excel', 'error')
            return redirect(url_for('manager.classes'))
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        return redirect(url_for('manager.classes'))

@bp.route('/students/export')
@login_required
@manager_required
def export_students():
    try:
        from app.utils.excel_export import export_students_to_excel
        students = Student.query.all()
        response = export_students_to_excel(students)
        if response:
            return response
        else:
            flash('Có lỗi xảy ra khi xuất file Excel', 'error')
            return redirect(url_for('manager.students'))
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        return redirect(url_for('manager.students'))

@bp.route('/schedule/export')
@login_required
@manager_required
def export_schedule():
    try:
        from app.utils.excel_export import export_schedule_to_excel
        schedules = Schedule.query.all()
        response = export_schedule_to_excel(schedules)
        if response:
            return response
        else:
            flash('Có lỗi xảy ra khi xuất file Excel', 'error')
            return redirect(url_for('manager.schedule'))
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        return redirect(url_for('manager.schedule'))

@bp.route('/manager/time_slots/add', methods=['GET', 'POST'])
@login_required
@manager_required
def add_time_slot():
    """Add new time slot"""
    form = TimeSlotForm()

    if form.validate_on_submit():
        # Check for time conflicts
        existing = TimeSlot.query.filter(
            TimeSlot.session_type == form.session_type.data,
            TimeSlot.is_active == True,
            db.or_(
                db.and_(TimeSlot.start_time <= form.start_time.data, TimeSlot.end_time > form.start_time.data),
                db.and_(TimeSlot.start_time < form.end_time.data, TimeSlot.end_time >= form.end_time.data),
                db.and_(TimeSlot.start_time >= form.start_time.data, TimeSlot.end_time <= form.end_time.data)
            )
        ).first()

        if existing:
            flash('Khung giờ bị trùng với khung giờ đã có', 'error')
        elif form.start_time.data >= form.end_time.data:
            flash('Giờ bắt đầu phải nhỏ hơn giờ kết thúc', 'error')
        else:
            time_slot = TimeSlot(
                name=form.name.data,
                session_type=form.session_type.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                description=form.description.data,
                created_by=current_user.id
            )

            db.session.add(time_slot)
            db.session.commit()

            flash('Thêm khung giờ thành công', 'success')
            return redirect(url_for('manager.time_slots'))

    return render_template('manager/add_time_slot.html',
                         title='Thêm khung giờ',
                         form=form)

@bp.route('/manager/time_slots/<int:slot_id>/edit', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_time_slot(slot_id):
    """Edit time slot"""
    time_slot = TimeSlot.query.get_or_404(slot_id)
    form = TimeSlotForm(obj=time_slot)

    if form.validate_on_submit():
        # Check for time conflicts (excluding current slot)
        existing = TimeSlot.query.filter(
            TimeSlot.id != slot_id,
            TimeSlot.session_type == form.session_type.data,
            TimeSlot.is_active == True,
            db.or_(
                db.and_(TimeSlot.start_time <= form.start_time.data, TimeSlot.end_time > form.start_time.data),
                db.and_(TimeSlot.start_time < form.end_time.data, TimeSlot.end_time >= form.end_time.data),
                db.and_(TimeSlot.start_time >= form.start_time.data, TimeSlot.end_time <= form.end_time.data)
            )
        ).first()

        if existing:
            flash('Khung giờ bị trùng với khung giờ đã có', 'error')
        elif form.start_time.data >= form.end_time.data:
            flash('Giờ bắt đầu phải nhỏ hơn giờ kết thúc', 'error')
        else:
            time_slot.name = form.name.data
            time_slot.session_type = form.session_type.data
            time_slot.start_time = form.start_time.data
            time_slot.end_time = form.end_time.data
            time_slot.description = form.description.data

            db.session.commit()

            flash('Cập nhật khung giờ thành công', 'success')
            return redirect(url_for('manager.time_slots'))

    return render_template('manager/edit_time_slot.html',
                         title='Sửa khung giờ',
                         form=form,
                         time_slot=time_slot)

@bp.route('/manager/time_slots/<int:slot_id>/delete', methods=['POST'])
@login_required
@manager_required
def delete_time_slot(slot_id):
    """Delete time slot"""
    time_slot = TimeSlot.query.get_or_404(slot_id)

    # Check if time slot is being used in schedules
    schedules_using = Schedule.query.filter_by(is_active=True).all()
    in_use = any(s.start_time == time_slot.start_time and s.end_time == time_slot.end_time for s in schedules_using)

    if in_use:
        flash('Không thể xóa khung giờ đang được sử dụng trong lịch dạy', 'error')
    else:
        time_slot.is_active = False
        db.session.commit()
        flash('Xóa khung giờ thành công', 'success')

    return redirect(url_for('manager.time_slots'))

@bp.route('/schedule/<int:schedule_id>/edit', methods=['GET'])
@login_required
@manager_required
def edit_schedule_form(schedule_id):
    """Show edit schedule form"""
    from app.forms.schedule_forms import ScheduleForm

    schedule = Schedule.query.get_or_404(schedule_id)

    # Check permissions
    if not current_user.is_admin() and schedule.class_obj.manager_id != current_user.id:
        abort(403)

    # Create form and populate with schedule data
    form = ScheduleForm()

    # Filter classes based on user role
    if current_user.is_admin():
        classes = Class.query.filter_by(is_active=True).all()
        form.class_id.choices = [(c.id, c.name) for c in classes]
    else:
        managed_classes = Class.query.filter_by(manager_id=current_user.id, is_active=True).all()
        form.class_id.choices = [(c.id, c.name) for c in managed_classes]

    # Populate form with schedule data
    form.class_id.data = schedule.class_id
    form.teacher_id.data = schedule.teacher_id
    form.day_of_week.data = schedule.day_of_week
    form.session.data = schedule.session
    form.start_time.data = schedule.start_time
    form.end_time.data = schedule.end_time
    form.subject.data = schedule.subject
    form.room.data = schedule.room

    return render_template('manager/schedule_form_tailwind.html',
                         title='Chỉnh sửa lịch dạy',
                         form=form,
                         schedule=schedule,
                         action='edit')

@bp.route('/schedule/<int:schedule_id>/edit', methods=['POST'])
@login_required
@manager_required
def edit_schedule(schedule_id):
    """Edit schedule"""
    schedule = Schedule.query.get_or_404(schedule_id)

    # Check permissions
    if not current_user.is_admin() and schedule.class_obj.manager_id != current_user.id:
        abort(403)

    # Handle form submission
    if request.method == 'POST':
        try:
            # Update schedule data from form
            schedule.class_id = request.form.get('class_id')
            schedule.teacher_id = request.form.get('teacher_id')
            schedule.day_of_week = int(request.form.get('day_of_week'))
            schedule.session = request.form.get('session')
            schedule.subject = request.form.get('subject')
            schedule.room = request.form.get('room')

            # Parse time fields
            start_time_str = request.form.get('start_time')
            end_time_str = request.form.get('end_time')

            if start_time_str and end_time_str:
                from datetime import datetime
                schedule.start_time = datetime.strptime(start_time_str, '%H:%M').time()
                schedule.end_time = datetime.strptime(end_time_str, '%H:%M').time()

            db.session.commit()
            flash('Cập nhật lịch dạy thành công!', 'success')
            return redirect(url_for('manager.schedule'))

        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
            return redirect(url_for('manager.schedule'))

@bp.route('/schedule/<int:schedule_id>/delete', methods=['POST'])
@login_required
@manager_required
def delete_schedule(schedule_id):
    """Delete schedule - Allow deletion even with active students"""
    from flask import jsonify

    schedule = Schedule.query.get_or_404(schedule_id)

    # Check permissions
    if not current_user.is_admin() and schedule.class_obj.manager_id != current_user.id:
        return jsonify({'success': False, 'message': 'Bạn không có quyền xóa lịch này'}), 403

    try:
        # Get enrolled students count for info message
        from app.models.student_schedule import StudentSchedule
        enrolled_students = StudentSchedule.query.filter_by(
            schedule_id=schedule_id,
            is_active=True
        ).count()

        # Get attendance count for info message
        from app.models.attendance import Attendance
        attendance_count = Attendance.query.filter_by(schedule_id=schedule_id).count()

        # Deactivate all student enrollments for this schedule
        StudentSchedule.query.filter_by(
            schedule_id=schedule_id,
            is_active=True
        ).update({'is_active': False})

        # Soft delete the schedule
        schedule.is_active = False
        db.session.commit()

        # Create informative message
        message = f'Xóa lịch dạy thành công'
        if enrolled_students > 0:
            message += f' (đã hủy đăng ký {enrolled_students} học sinh)'
        if attendance_count > 0:
            message += f' (có {attendance_count} bản ghi điểm danh)'

        return jsonify({'success': True, 'message': message})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'})

@bp.route('/notification/generator')
@login_required
@manager_required
def notification_generator():
    from datetime import date
    classes = Class.query.filter_by(is_active=True).all()
    today = date.today().strftime('%Y-%m-%d')

    return render_template('manager/notification_generator_tailwind.html',
                         title='Tạo thông báo lịch học',
                         classes=classes,
                         today=today)

@bp.route('/events/export')
@login_required
@manager_required
def export_events():
    """Export events to Excel"""
    try:
        from app.utils.excel_export import export_events_to_excel
        events = Event.query.filter_by(is_active=True).order_by(Event.start_datetime.desc()).all()
        response = export_events_to_excel(events)
        if response:
            return response
        else:
            flash('Có lỗi xảy ra khi xuất file Excel', 'error')
            return redirect(url_for('main.dashboard'))
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@bp.route('/notification/generate', methods=['POST'])
@login_required
@manager_required
def generate_notification():
    try:
        notification_date = request.form.get('notification_date')
        class_id = request.form.get('class_id')
        template_type = request.form.get('template_type')
        custom_message = request.form.get('custom_message')
        include_teacher = request.form.get('include_teacher') == 'on'
        include_time = request.form.get('include_time') == 'on'
        include_contact = request.form.get('include_contact') == 'on'

        if not notification_date or not template_type:
            return jsonify({'success': False, 'message': 'Thiếu thông tin bắt buộc'})

        # Parse date
        from datetime import datetime
        try:
            date_obj = datetime.strptime(notification_date, '%Y-%m-%d')
            day_of_week = date_obj.weekday() + 1  # Monday = 1, Sunday = 0 -> 7
            if day_of_week == 7:  # Sunday
                day_of_week = 0
            date_str = date_obj.strftime('%d/%m/%Y')
            day_name = {
                1: 'Thứ Hai', 2: 'Thứ Ba', 3: 'Thứ Tư', 4: 'Thứ Năm',
                5: 'Thứ Sáu', 6: 'Thứ Bảy', 0: 'Chủ Nhật'
            }.get(day_of_week, f'Thứ {day_of_week}')

            # Calculate week number for the selected date
            year, week_num, _ = date_obj.isocalendar()
            week_number = f"{year}-W{week_num:02d}"

        except ValueError:
            return jsonify({'success': False, 'message': 'Định dạng ngày không hợp lệ'})

        # Get schedules for the specific date and week
        query = Schedule.query.filter_by(
            day_of_week=day_of_week,
            week_number=week_number,
            is_active=True
        )
        if class_id:
            query = query.filter_by(class_id=int(class_id))

        schedules = query.order_by(Schedule.session, Schedule.start_time).all()

        # Generate notification based on template type
        if template_type == 'custom':
            notification = custom_message or 'Nội dung thông báo tùy chỉnh'

        elif template_type == 'daily':
            notification = f"📚 THÔNG BÁO LỊCH HỌC\n"
            notification += f"📅 Ngày: {day_name}, {date_str}\n\n"

            if schedules:
                notification += "📋 LỊCH HỌC HÔM NAY:\n"
                for i, schedule in enumerate(schedules, 1):
                    notification += f"\n{i}. Lớp: {schedule.class_obj.name}\n"
                    if include_time:
                        notification += f"   ⏰ Thời gian: {schedule.start_time.strftime('%H:%M')} - {schedule.end_time.strftime('%H:%M')}\n"
                    if include_teacher:
                        notification += f"   👨‍🏫 Giáo viên: {schedule.teacher.full_name}\n"
                    if schedule.room:
                        notification += f"   📍 Phòng: {schedule.room}\n"
                    else:
                        notification += f"   📍 Buổi: {schedule.session_name}\n"
            else:
                notification += "ℹ️ Hôm nay không có lịch học.\n"

            notification += "\n📞 Mọi thắc mắc xin liên hệ văn phòng."

        elif template_type == 'reminder':
            notification = f"💰 THÔNG BÁO HỌC PHÍ\n\n"
            notification += f"Kính gửi Quý Phụ huynh,\n\n"
            notification += f"Trung tâm xin thông báo về việc đóng học phí tháng {date_obj.strftime('%m/%Y')}:\n\n"
            notification += f"📅 Hạn đóng: {date_str}\n"
            notification += f"💵 Học phí: [Số tiền]\n"
            notification += f"🏦 Tài khoản: [Số tài khoản]\n"
            notification += f"📝 Nội dung CK: [Tên học sinh] - Học phí tháng {date_obj.strftime('%m/%Y')}\n\n"
            notification += f"Quý phụ huynh vui lòng đóng học phí đúng hạn.\n"
            notification += f"📞 Liên hệ: [Số điện thoại] để được hỗ trợ."

        else:
            notification = f"📚 THÔNG BÁO\n\n"
            notification += f"Nội dung thông báo sẽ được cập nhật.\n"
            notification += f"📞 Mọi thắc mắc xin liên hệ văn phòng."

        # Add contact info if requested
        if include_contact:
            notification += f"\n\n📞 THÔNG TIN LIÊN HỆ:\n"
            notification += f"📱 Hotline: [Số điện thoại]\n"
            notification += f"📧 Email: [Email liên hệ]\n"
            notification += f"🌐 Website: [Website]\n"
            notification += f"📍 Địa chỉ: [Địa chỉ trung tâm]"

        return jsonify({'success': True, 'notification': notification})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'})


