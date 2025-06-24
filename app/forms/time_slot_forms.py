from flask_wtf import FlaskForm
from wtforms import StringField, TimeField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class TimeSlotForm(FlaskForm):
    """Form for creating/editing time slots"""
    name = StringField('Tên khung giờ', validators=[
        DataRequired(message='Vui lòng nhập tên khung giờ'),
        Length(min=2, max=50, message='Tên khung giờ phải từ 2-50 ký tự')
    ])
    
    session_type = SelectField('Loại buổi', choices=[
        ('morning', 'Buổi sáng'),
        ('afternoon', 'Buổi chiều'),
        ('evening', 'Buổi tối')
    ], validators=[DataRequired(message='Vui lòng chọn loại buổi')])
    
    start_time = TimeField('Giờ bắt đầu', validators=[
        DataRequired(message='Vui lòng nhập giờ bắt đầu')
    ])
    
    end_time = TimeField('Giờ kết thúc', validators=[
        DataRequired(message='Vui lòng nhập giờ kết thúc')
    ])
    
    description = TextAreaField('Mô tả', validators=[
        Length(max=200, message='Mô tả không được quá 200 ký tự')
    ])
    
    submit = SubmitField('Lưu khung giờ')
