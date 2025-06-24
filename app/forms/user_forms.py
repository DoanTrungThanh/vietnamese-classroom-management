from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SelectMultipleField, TextAreaField, BooleanField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from app.models.user import User

class CreateUserForm(FlaskForm):
    full_name = StringField('Họ và tên', validators=[
        DataRequired(message='Vui lòng nhập họ và tên'),
        Length(min=2, max=100, message='Họ và tên phải từ 2-100 ký tự')
    ])
    
    username = StringField('Tên đăng nhập', validators=[
        DataRequired(message='Vui lòng nhập tên đăng nhập'),
        Length(min=3, max=50, message='Tên đăng nhập phải từ 3-50 ký tự')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Vui lòng nhập email'),
        Email(message='Email không hợp lệ'),
        Length(max=120, message='Email không được quá 120 ký tự')
    ])
    
    phone = StringField('Số điện thoại', validators=[
        Optional(),
        Length(max=20, message='Số điện thoại không được quá 20 ký tự')
    ])
    
    date_of_birth = DateField('Ngày sinh', validators=[Optional()])
    
    address = TextAreaField('Địa chỉ', validators=[
        Optional(),
        Length(max=500, message='Địa chỉ không được quá 500 ký tự')
    ])
    
    role = SelectField('Vai trò', choices=[
        ('admin', 'Quản trị viên'),
        ('manager', 'Quản sinh'),
        ('teacher', 'Giáo viên')
    ], validators=[DataRequired(message='Vui lòng chọn vai trò')])
    
    password = PasswordField('Mật khẩu', validators=[
        DataRequired(message='Vui lòng nhập mật khẩu'),
        Length(min=8, message='Mật khẩu phải có ít nhất 8 ký tự')
    ])
    
    password_confirm = PasswordField('Xác nhận mật khẩu', validators=[
        DataRequired(message='Vui lòng xác nhận mật khẩu'),
        EqualTo('password', message='Mật khẩu không khớp')
    ])
    
    is_active = BooleanField('Kích hoạt tài khoản', default=True)
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Tên đăng nhập đã tồn tại')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email đã được sử dụng')

class EditUserForm(FlaskForm):
    full_name = StringField('Họ và tên', validators=[
        DataRequired(message='Vui lòng nhập họ và tên'),
        Length(min=2, max=100, message='Họ và tên phải từ 2-100 ký tự')
    ])
    
    username = StringField('Tên đăng nhập', validators=[
        DataRequired(message='Vui lòng nhập tên đăng nhập'),
        Length(min=3, max=50, message='Tên đăng nhập phải từ 3-50 ký tự')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Vui lòng nhập email'),
        Email(message='Email không hợp lệ'),
        Length(max=120, message='Email không được quá 120 ký tự')
    ])
    
    phone = StringField('Số điện thoại', validators=[
        Optional(),
        Length(max=20, message='Số điện thoại không được quá 20 ký tự')
    ])
    
    date_of_birth = DateField('Ngày sinh', validators=[Optional()])
    
    address = TextAreaField('Địa chỉ', validators=[
        Optional(),
        Length(max=500, message='Địa chỉ không được quá 500 ký tự')
    ])
    
    role = SelectField('Vai trò', choices=[
        ('admin', 'Quản trị viên'),
        ('manager', 'Quản sinh'),
        ('teacher', 'Giáo viên')
    ], validators=[DataRequired(message='Vui lòng chọn vai trò')])
    
    password = PasswordField('Mật khẩu mới', validators=[
        Optional(),
        Length(min=8, message='Mật khẩu phải có ít nhất 8 ký tự')
    ])
    
    password_confirm = PasswordField('Xác nhận mật khẩu mới', validators=[
        EqualTo('password', message='Mật khẩu không khớp')
    ])
    
    is_active = BooleanField('Kích hoạt tài khoản')
    
    def __init__(self, user, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.user = user
    
    def validate_username(self, username):
        if username.data != self.user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Tên đăng nhập đã tồn tại')
    
    def validate_email(self, email):
        if email.data != self.user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email đã được sử dụng')

class CreateClassForm(FlaskForm):
    name = StringField('Tên lớp', validators=[
        DataRequired(message='Vui lòng nhập tên lớp'),
        Length(min=2, max=100, message='Tên lớp phải từ 2-100 ký tự')
    ])
    
    description = TextAreaField('Mô tả', validators=[
        Optional(),
        Length(max=500, message='Mô tả không được quá 500 ký tự')
    ])
    
    manager_id = SelectField('Quản sinh', coerce=int, validators=[
        Optional()
    ])

    is_active = BooleanField('Kích hoạt lớp', default=True)
    
    def __init__(self, *args, **kwargs):
        super(CreateClassForm, self).__init__(*args, **kwargs)
        # Populate manager choices
        from app.models.user import User
        managers = User.query.filter_by(role='manager', is_active=True).all()
        self.manager_id.choices = [(0, 'Chọn quản sinh')] + [(m.id, m.full_name) for m in managers]

class EditClassForm(FlaskForm):
    name = StringField('Tên lớp', validators=[
        DataRequired(message='Vui lòng nhập tên lớp'),
        Length(min=2, max=100, message='Tên lớp phải từ 2-100 ký tự')
    ])
    
    description = TextAreaField('Mô tả', validators=[
        Optional(),
        Length(max=500, message='Mô tả không được quá 500 ký tự')
    ])
    
    manager_id = SelectField('Quản sinh', coerce=int, validators=[
        Optional()
    ])

    is_active = BooleanField('Kích hoạt lớp')
    
    def __init__(self, *args, **kwargs):
        super(EditClassForm, self).__init__(*args, **kwargs)
        # Populate manager choices
        from app.models.user import User
        managers = User.query.filter_by(role='manager', is_active=True).all()
        self.manager_id.choices = [(0, 'Chọn quản sinh')] + [(m.id, m.full_name) for m in managers]

class CreateStudentForm(FlaskForm):
    full_name = StringField('Họ và tên', validators=[
        DataRequired(message='Vui lòng nhập họ và tên'),
        Length(min=2, max=100, message='Họ và tên phải từ 2-100 ký tự')
    ])
    
    student_code = StringField('Mã học sinh', validators=[
        Optional(),
        Length(max=20, message='Mã học sinh không được quá 20 ký tự')
    ], render_kw={'readonly': True, 'placeholder': 'Mã sẽ được tự động cấp phát bằng hash từ 1000'})
    
    date_of_birth = DateField('Ngày sinh', validators=[Optional()])
    
    # class_id removed - students don't belong to specific classes initially
    # They will be assigned through schedule assignments
    
    parent_name = StringField('Tên phụ huynh', validators=[
        Optional(),
        Length(max=100, message='Tên phụ huynh không được quá 100 ký tự')
    ])
    
    parent_phone = StringField('SĐT phụ huynh', validators=[
        Optional(),
        Length(max=20, message='SĐT phụ huynh không được quá 20 ký tự')
    ])
    
    address = TextAreaField('Địa chỉ', validators=[
        Optional(),
        Length(max=500, message='Địa chỉ không được quá 500 ký tự')
    ])

    profile_url = StringField('Link hồ sơ (Google Drive)', validators=[
        Optional(),
        Length(max=500, message='Link không được quá 500 ký tự')
    ])

    is_active = BooleanField('Đang học', default=True)

    submit = SubmitField('Thêm học sinh')
    
    # No __init__ needed since we removed class_id field

class EditStudentForm(FlaskForm):
    full_name = StringField('Họ và tên', validators=[
        DataRequired(message='Vui lòng nhập họ và tên'),
        Length(min=2, max=100, message='Họ và tên phải từ 2-100 ký tự')
    ])
    
    student_code = StringField('Mã học sinh *', validators=[
        DataRequired(message='Vui lòng nhập mã học sinh'),
        Length(min=3, max=20, message='Mã học sinh phải từ 3-20 ký tự')
    ])
    
    date_of_birth = DateField('Ngày sinh', validators=[Optional()])
    
    class_id = SelectField('Lớp học', coerce=int, validators=[
        Optional()
    ])
    
    parent_name = StringField('Tên phụ huynh', validators=[
        Optional(),
        Length(max=100, message='Tên phụ huynh không được quá 100 ký tự')
    ])
    
    parent_phone = StringField('SĐT phụ huynh', validators=[
        Optional(),
        Length(max=20, message='SĐT phụ huynh không được quá 20 ký tự')
    ])
    
    address = TextAreaField('Địa chỉ', validators=[
        Optional(),
        Length(max=500, message='Địa chỉ không được quá 500 ký tự')
    ])

    profile_url = StringField('Link hồ sơ (Google Drive)', validators=[
        Optional(),
        Length(max=500, message='Link không được quá 500 ký tự')
    ])

    is_active = BooleanField('Đang học')

    submit = SubmitField('Cập nhật học sinh')
    
    def __init__(self, *args, **kwargs):
        super(EditStudentForm, self).__init__(*args, **kwargs)
        # Populate class choices
        from app.models.class_model import Class
        classes = Class.query.filter_by(is_active=True).all()
        self.class_id.choices = [(0, 'Chọn lớp học')] + [(c.id, c.name) for c in classes]

class AddStudentsToClassForm(FlaskForm):
    """Form for adding students to class"""
    student_ids = SelectMultipleField('Học sinh', coerce=int, validators=[
        DataRequired(message='Vui lòng chọn ít nhất một học sinh')
    ])

    submit = SubmitField('Thêm vào lớp')

    def __init__(self, available_students=None, *args, **kwargs):
        super(AddStudentsToClassForm, self).__init__(*args, **kwargs)
        if available_students:
            self.student_ids.choices = [(s.id, f"{s.full_name} ({s.student_code})") for s in available_students]
        else:
            self.student_ids.choices = []
