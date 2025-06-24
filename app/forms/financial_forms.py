from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, DateField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from datetime import date

class FinancialTransactionForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Mô tả', validators=[Optional(), Length(max=500)])
    amount = DecimalField('Số tiền', validators=[DataRequired(), NumberRange(min=0.01)])
    transaction_date = DateField('Ngày giao dịch', validators=[DataRequired()], default=date.today)
    transaction_type = SelectField('Loại giao dịch', choices=[
        ('income', 'Khoản thu'),
        ('expense', 'Khoản chi')
    ], validators=[DataRequired()])
    category = SelectField('Danh mục', choices=[
        ('tuition', 'Học phí'),
        ('donation', 'Quyên góp'),
        ('event', 'Sự kiện'),
        ('other_income', 'Thu nhập khác'),
        ('office_supplies', 'Văn phòng phẩm'),
        ('utilities', 'Tiện ích'),
        ('maintenance', 'Bảo trì'),
        ('salary', 'Lương'),
        ('other_expense', 'Chi phí khác')
    ], validators=[DataRequired()])
    payment_method = SelectField('Phương thức thanh toán', choices=[
        ('cash', 'Tiền mặt'),
        ('bank_transfer', 'Chuyển khoản'),
        ('card', 'Thẻ'),
        ('other', 'Khác')
    ], validators=[DataRequired()])
    receipt_number = StringField('Số hóa đơn', validators=[Optional(), Length(max=50)])
    vendor_payer = StringField('Nhà cung cấp/Người trả', validators=[Optional(), Length(max=200)])
    notes = TextAreaField('Ghi chú', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Lưu')

class DonationAssetForm(FlaskForm):
    asset_name = StringField('Tên tài sản', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Mô tả', validators=[Optional(), Length(max=500)])
    category = SelectField('Danh mục', choices=[
        ('equipment', 'Thiết bị'),
        ('books', 'Sách vở'),
        ('supplies', 'Đồ dùng'),
        ('furniture', 'Nội thất'),
        ('electronics', 'Điện tử'),
        ('clothing', 'Quần áo'),
        ('food', 'Thực phẩm'),
        ('other', 'Khác')
    ], validators=[DataRequired()])
    quantity = IntegerField('Số lượng', validators=[DataRequired(), NumberRange(min=1)], default=1)
    estimated_value = DecimalField('Giá trị ước tính', validators=[Optional(), NumberRange(min=0)])
    condition = SelectField('Tình trạng', choices=[
        ('new', 'Mới'),
        ('good', 'Tốt'),
        ('fair', 'Khá'),
        ('poor', 'Kém')
    ], validators=[DataRequired()])
    
    # Donor information
    donor_name = StringField('Tên người quyên góp', validators=[Optional(), Length(max=200)])
    donor_phone = StringField('Số điện thoại', validators=[Optional(), Length(max=20)])
    donor_address = TextAreaField('Địa chỉ', validators=[Optional(), Length(max=300)])
    donation_date = DateField('Ngày quyên góp', validators=[DataRequired()], default=date.today)
    
    # Storage
    location = StringField('Vị trí lưu trữ', validators=[Optional(), Length(max=200)])
    notes = TextAreaField('Ghi chú', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Lưu')

class AssetDistributionForm(FlaskForm):
    distributed_to = StringField('Phân phối cho', validators=[DataRequired(), Length(max=200)])
    distributed_date = DateField('Ngày phân phối', validators=[DataRequired()], default=date.today)
    distribution_notes = TextAreaField('Ghi chú phân phối', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Phân phối')

class AssetStatusUpdateForm(FlaskForm):
    status = SelectField('Trạng thái', choices=[
        ('received', 'Đã nhận'),
        ('distributed', 'Đã phân phối'),
        ('damaged', 'Hư hỏng'),
        ('lost', 'Mất')
    ], validators=[DataRequired()])
    notes = TextAreaField('Ghi chú', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Cập nhật')

class DonationRecordForm(FlaskForm):
    record_type = SelectField('Loại bản ghi', choices=[
        ('received', 'Nhận quyên góp'),
        ('given', 'Trao quyên góp')
    ], validators=[DataRequired()])
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Mô tả', validators=[Optional(), Length(max=500)])
    amount = DecimalField('Số tiền', validators=[Optional(), NumberRange(min=0)])
    transaction_date = DateField('Ngày giao dịch', validators=[DataRequired()], default=date.today)
    category = SelectField('Danh mục', choices=[
        ('cash', 'Tiền mặt'),
        ('goods', 'Hiện vật'),
        ('scholarship', 'Học bổng'),
        ('equipment', 'Thiết bị'),
        ('other', 'Khác')
    ], validators=[DataRequired()])
    purpose = StringField('Mục đích', validators=[Optional(), Length(max=200)])

    # Donor information (for received donations)
    donor_name = StringField('Tên người quyên góp', validators=[Optional(), Length(max=200)])
    donor_phone = StringField('Số điện thoại người quyên góp', validators=[Optional(), Length(max=20)])
    donor_address = TextAreaField('Địa chỉ người quyên góp', validators=[Optional(), Length(max=300)])

    # Recipient information (for given donations)
    recipient_name = StringField('Tên người nhận', validators=[Optional(), Length(max=200)])
    recipient_phone = StringField('Số điện thoại người nhận', validators=[Optional(), Length(max=20)])
    recipient_address = TextAreaField('Địa chỉ người nhận', validators=[Optional(), Length(max=300)])

    receipt_number = StringField('Số biên nhận', validators=[Optional(), Length(max=50)])
    notes = TextAreaField('Ghi chú', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Lưu')

class FinancialReportForm(FlaskForm):
    start_date = DateField('Từ ngày', validators=[DataRequired()])
    end_date = DateField('Đến ngày', validators=[DataRequired()])
    transaction_type = SelectField('Loại giao dịch', choices=[
        ('', 'Tất cả'),
        ('income', 'Khoản thu'),
        ('expense', 'Khoản chi')
    ], validators=[Optional()])
    category = SelectField('Danh mục', choices=[
        ('', 'Tất cả'),
        ('tuition', 'Học phí'),
        ('donation', 'Quyên góp'),
        ('event', 'Sự kiện'),
        ('office_supplies', 'Văn phòng phẩm'),
        ('utilities', 'Tiện ích'),
        ('maintenance', 'Bảo trì'),
        ('salary', 'Lương'),
        ('other', 'Khác')
    ], validators=[Optional()])
    submit = SubmitField('Tạo báo cáo')
