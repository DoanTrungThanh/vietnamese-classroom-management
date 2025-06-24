from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, DateField, BooleanField
from wtforms.validators import DataRequired, Length
from app.models.user import User

class ClassForm(FlaskForm):
    name = StringField('Tên lớp', validators=[DataRequired(), Length(min=1, max=50)])
    block_name = StringField('Khối lớp', validators=[DataRequired(), Length(min=1, max=50)])
    description = TextAreaField('Mô tả')
    manager_id = SelectField('Quản sinh', coerce=int)
    is_active = BooleanField('Kích hoạt', default=True)
    submit = SubmitField('Lưu')
    
    def __init__(self, *args, **kwargs):
        super(ClassForm, self).__init__(*args, **kwargs)
        self.manager_id.choices = [(0, 'Chọn quản sinh')] + [
            (u.id, u.full_name) for u in User.query.filter_by(role='manager', is_active=True).all()
        ]

class StudentForm(FlaskForm):
    student_code = StringField('Mã học sinh', validators=[DataRequired(), Length(min=1, max=20)])
    full_name = StringField('Họ và tên', validators=[DataRequired(), Length(min=1, max=100)])
    date_of_birth = DateField('Ngày sinh')
    address = TextAreaField('Địa chỉ')
    parent_name = StringField('Tên phụ huynh', validators=[Length(max=100)])
    parent_phone = StringField('SĐT phụ huynh', validators=[Length(max=20)])
    profile_url = StringField('Đường dẫn hồ sơ', validators=[Length(max=500)])
    class_id = SelectField('Lớp học', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Lưu')

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        # Choices will be set in the route based on user permissions
        self.class_id.choices = []
