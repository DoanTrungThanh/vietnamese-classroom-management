from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Length

class EventForm(FlaskForm):
    name = StringField('Tên sự kiện', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Mô tả')
    start_datetime = DateTimeField('Thời gian bắt đầu', validators=[DataRequired()], 
                                  format='%Y-%m-%d %H:%M')
    end_datetime = DateTimeField('Thời gian kết thúc', validators=[DataRequired()], 
                                format='%Y-%m-%d %H:%M')
    location = StringField('Địa điểm', validators=[Length(max=200)])
    submit = SubmitField('Lưu')
