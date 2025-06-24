from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TimeField, TextAreaField, SubmitField, DateField, HiddenField
from wtforms.validators import DataRequired, Length
from app.models.user import User
from app.models.class_model import Class
from datetime import datetime, timedelta

class ScheduleForm(FlaskForm):
    class_id = SelectField('Lớp học', coerce=int, validators=[DataRequired()])
    teacher_id = SelectField('Giáo viên', coerce=int, validators=[DataRequired()])
    week_number = SelectField('Tuần học', validators=[DataRequired()])
    day_of_week = SelectField('Thứ', choices=[
        (1, 'Thứ 2'), (2, 'Thứ 3'), (3, 'Thứ 4'), (4, 'Thứ 5'),
        (5, 'Thứ 6'), (6, 'Thứ 7'), (7, 'Chủ nhật')
    ], coerce=int, validators=[DataRequired()])
    session = SelectField('Khung giờ', choices=[
        ('morning', 'Buổi sáng (07:30 - 11:30)'),
        ('afternoon', 'Buổi chiều (13:30 - 17:30)'),
        ('evening', 'Buổi tối (18:30 - 21:30)')
    ], validators=[DataRequired()])
    start_time = TimeField('Giờ bắt đầu', validators=[DataRequired()])
    end_time = TimeField('Giờ kết thúc', validators=[DataRequired()])
    subject = StringField('Môn học', validators=[Length(max=100)])
    room = StringField('Phòng học', validators=[Length(max=50)])
    submit = SubmitField('Lưu')
    
    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.class_id.choices = [
            (c.id, c.name)
            for c in Class.query.filter_by(is_active=True).all()
        ]
        self.teacher_id.choices = [
            (u.id, u.full_name)
            for u in User.query.filter_by(role='teacher', is_active=True).all()
        ]

        # Generate week choices (current week + next 8 weeks)
        week_choices = []
        current_date = datetime.now()
        for i in range(9):  # Current week + 8 future weeks
            week_date = current_date + timedelta(weeks=i)
            year, week, _ = week_date.isocalendar()
            week_str = f"{year}-W{week:02d}"

            # Calculate week start date for display
            week_start = week_date - timedelta(days=week_date.weekday())
            week_end = week_start + timedelta(days=6)

            display_text = f"Tuần {week} ({week_start.strftime('%d/%m')} - {week_end.strftime('%d/%m/%Y')})"
            week_choices.append((week_str, display_text))

        self.week_number.choices = week_choices

class CopyScheduleForm(FlaskForm):
    source_week = SelectField('Tuần nguồn', validators=[DataRequired()])
    target_week = SelectField('Tuần đích', validators=[DataRequired()])
    copy_all = SelectField('Sao chép', choices=[
        ('all', 'Tất cả lịch dạy'),
        ('class', 'Chỉ lịch của lớp cụ thể')
    ], validators=[DataRequired()])
    class_id = SelectField('Lớp học (tùy chọn)', coerce=int)
    submit = SubmitField('Sao chép lịch')

    def __init__(self, *args, **kwargs):
        super(CopyScheduleForm, self).__init__(*args, **kwargs)

        # Generate week choices for source and target
        week_choices = []
        current_date = datetime.now()

        # Add past 4 weeks + current week + next 8 weeks
        for i in range(-4, 9):
            week_date = current_date + timedelta(weeks=i)
            year, week, _ = week_date.isocalendar()
            week_str = f"{year}-W{week:02d}"

            # Calculate week start date for display
            week_start = week_date - timedelta(days=week_date.weekday())
            week_end = week_start + timedelta(days=6)

            if i == 0:
                display_text = f"Tuần {week} - Tuần hiện tại ({week_start.strftime('%d/%m')} - {week_end.strftime('%d/%m/%Y')})"
            elif i < 0:
                display_text = f"Tuần {week} ({week_start.strftime('%d/%m')} - {week_end.strftime('%d/%m/%Y')})"
            else:
                display_text = f"Tuần {week} ({week_start.strftime('%d/%m')} - {week_end.strftime('%d/%m/%Y')})"

            week_choices.append((week_str, display_text))

        self.source_week.choices = week_choices
        self.target_week.choices = week_choices

        # Class choices
        self.class_id.choices = [(0, 'Tất cả lớp')] + [
            (c.id, c.name)
            for c in Class.query.filter_by(is_active=True).all()
        ]

class AttendanceForm(FlaskForm):
    schedule_id = HiddenField()
    date = DateField('Ngày', validators=[DataRequired()])
    lesson_content = TextAreaField('Nội dung bài giảng')
    notes = TextAreaField('Ghi chú')
    submit = SubmitField('Lưu điểm danh')
