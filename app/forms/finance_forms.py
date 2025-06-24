from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, TextAreaField, StringField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from app.models.class_model import Class
from app.models.event import Event

class FinanceForm(FlaskForm):
    type = SelectField('Loại', choices=[
        ('income', 'Thu'),
        ('expense', 'Chi')
    ], validators=[DataRequired()])
    amount = FloatField('Số tiền', validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField('Mô tả', validators=[DataRequired()])
    category = StringField('Danh mục')
    class_id = SelectField('Lớp học (tùy chọn)', coerce=int)
    event_id = SelectField('Sự kiện (tùy chọn)', coerce=int)
    transaction_date = DateField('Ngày giao dịch', validators=[DataRequired()])
    submit = SubmitField('Lưu')
    
    def __init__(self, *args, **kwargs):
        super(FinanceForm, self).__init__(*args, **kwargs)
        self.class_id.choices = [(0, 'Không chọn')] + [
            (c.id, f"{c.name} - {c.block_name}") 
            for c in Class.query.filter_by(is_active=True).all()
        ]
        self.event_id.choices = [(0, 'Không chọn')] + [
            (e.id, e.name) 
            for e in Event.query.filter_by(is_active=True).all()
        ]
