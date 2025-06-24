from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, DateField, SelectField, HiddenField
from wtforms.validators import DataRequired, NumberRange, Length, Optional, ValidationError
from datetime import date

class ExpenseCategoryForm(FlaskForm):
    name = StringField('Tên danh mục', validators=[
        DataRequired(message='Vui lòng nhập tên danh mục'),
        Length(min=2, max=100, message='Tên danh mục phải từ 2-100 ký tự')
    ])
    
    description = TextAreaField('Mô tả', validators=[
        Optional(),
        Length(max=500, message='Mô tả không được quá 500 ký tự')
    ])
    
    color = StringField('Màu sắc', validators=[
        Optional(),
        Length(min=7, max=7, message='Mã màu phải có 7 ký tự')
    ])

class ExpenseForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[
        DataRequired(message='Vui lòng nhập tiêu đề'),
        Length(min=2, max=200, message='Tiêu đề phải từ 2-200 ký tự')
    ])
    
    description = TextAreaField('Mô tả chi tiết', validators=[
        Optional(),
        Length(max=1000, message='Mô tả không được quá 1000 ký tự')
    ])
    
    amount = DecimalField('Số tiền', validators=[
        DataRequired(message='Vui lòng nhập số tiền'),
        NumberRange(min=0.01, message='Số tiền phải lớn hơn 0')
    ], places=2)
    
    expense_date = DateField('Ngày chi tiêu', validators=[
        DataRequired(message='Vui lòng chọn ngày chi tiêu')
    ], default=date.today)
    
    category_id = SelectField('Danh mục', coerce=int, validators=[
        DataRequired(message='Vui lòng chọn danh mục')
    ])
    
    receipt_number = StringField('Số hóa đơn', validators=[
        Optional(),
        Length(max=50, message='Số hóa đơn không được quá 50 ký tự')
    ])
    
    vendor = StringField('Nhà cung cấp', validators=[
        Optional(),
        Length(max=200, message='Tên nhà cung cấp không được quá 200 ký tự')
    ])
    
    payment_method = SelectField('Phương thức thanh toán', choices=[
        ('cash', 'Tiền mặt'),
        ('bank_transfer', 'Chuyển khoản'),
        ('card', 'Thẻ'),
        ('other', 'Khác')
    ], validators=[DataRequired(message='Vui lòng chọn phương thức thanh toán')])
    
    notes = TextAreaField('Ghi chú', validators=[
        Optional(),
        Length(max=500, message='Ghi chú không được quá 500 ký tự')
    ])
    
    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        # Populate category choices
        from app.models.expense import ExpenseCategory
        categories = ExpenseCategory.query.filter_by(is_active=True).all()
        self.category_id.choices = [(c.id, c.name) for c in categories]

class BudgetForm(FlaskForm):
    name = StringField('Tên ngân sách', validators=[
        DataRequired(message='Vui lòng nhập tên ngân sách'),
        Length(min=2, max=200, message='Tên ngân sách phải từ 2-200 ký tự')
    ])
    
    description = TextAreaField('Mô tả', validators=[
        Optional(),
        Length(max=500, message='Mô tả không được quá 500 ký tự')
    ])
    
    total_amount = DecimalField('Tổng ngân sách', validators=[
        DataRequired(message='Vui lòng nhập tổng ngân sách'),
        NumberRange(min=0.01, message='Ngân sách phải lớn hơn 0')
    ], places=2)
    
    start_date = DateField('Ngày bắt đầu', validators=[
        DataRequired(message='Vui lòng chọn ngày bắt đầu')
    ])
    
    end_date = DateField('Ngày kết thúc', validators=[
        DataRequired(message='Vui lòng chọn ngày kết thúc')
    ])
    
    category_id = SelectField('Danh mục (tùy chọn)', coerce=int, validators=[
        Optional()
    ])
    
    def __init__(self, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)
        # Populate category choices
        from app.models.expense import ExpenseCategory
        categories = ExpenseCategory.query.filter_by(is_active=True).all()
        self.category_id.choices = [(0, 'Tất cả danh mục')] + [(c.id, c.name) for c in categories]
    
    def validate_end_date(self, end_date):
        if end_date.data <= self.start_date.data:
            raise ValidationError('Ngày kết thúc phải sau ngày bắt đầu')

class ExpenseApprovalForm(FlaskForm):
    status = SelectField('Trạng thái', choices=[
        ('approved', 'Duyệt'),
        ('rejected', 'Từ chối')
    ], validators=[DataRequired(message='Vui lòng chọn trạng thái')])
    
    notes = TextAreaField('Ghi chú duyệt', validators=[
        Optional(),
        Length(max=500, message='Ghi chú không được quá 500 ký tự')
    ])

class ExpenseFilterForm(FlaskForm):
    start_date = DateField('Từ ngày', validators=[Optional()])
    end_date = DateField('Đến ngày', validators=[Optional()])
    category_id = SelectField('Danh mục', coerce=int, validators=[Optional()])
    status = SelectField('Trạng thái', validators=[Optional()])
    payment_method = SelectField('Phương thức thanh toán', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(ExpenseFilterForm, self).__init__(*args, **kwargs)
        
        # Populate category choices
        from app.models.expense import ExpenseCategory
        categories = ExpenseCategory.query.filter_by(is_active=True).all()
        self.category_id.choices = [(0, 'Tất cả danh mục')] + [(c.id, c.name) for c in categories]
        
        # Status choices
        self.status.choices = [
            ('', 'Tất cả trạng thái'),
            ('pending', 'Chờ duyệt'),
            ('approved', 'Đã duyệt'),
            ('rejected', 'Từ chối')
        ]
        
        # Payment method choices
        self.payment_method.choices = [
            ('', 'Tất cả phương thức'),
            ('cash', 'Tiền mặt'),
            ('bank_transfer', 'Chuyển khoản'),
            ('card', 'Thẻ'),
            ('other', 'Khác')
        ]
