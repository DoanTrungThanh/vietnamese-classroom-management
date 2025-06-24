from app import db
from datetime import datetime

class FinancialTransaction(db.Model):
    """Model for income and expense transactions"""
    __tablename__ = 'financial_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    category = db.Column(db.String(100))  # Học phí, Quyên góp, Văn phòng phẩm, etc.
    payment_method = db.Column(db.String(50))  # cash, bank_transfer, card, etc.
    receipt_number = db.Column(db.String(50))
    vendor_payer = db.Column(db.String(200))  # Vendor for expense, Payer for income
    status = db.Column(db.String(20), default='approved')  # pending, approved, rejected
    notes = db.Column(db.Text)
    
    # Foreign Keys
    created_by = db.Column(db.Integer, nullable=False)
    approved_by = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    
    @property
    def transaction_type_display(self):
        type_map = {
            'income': 'Khoản thu',
            'expense': 'Khoản chi'
        }
        return type_map.get(self.transaction_type, self.transaction_type)
    
    @property
    def status_display(self):
        status_map = {
            'pending': 'Chờ duyệt',
            'approved': 'Đã duyệt',
            'rejected': 'Từ chối'
        }
        return status_map.get(self.status, self.status)
    
    @property
    def payment_method_display(self):
        method_map = {
            'cash': 'Tiền mặt',
            'bank_transfer': 'Chuyển khoản',
            'card': 'Thẻ',
            'other': 'Khác'
        }
        return method_map.get(self.payment_method, self.payment_method)
    
    def __repr__(self):
        return f'<FinancialTransaction {self.transaction_type}: {self.title} - {self.amount}>'

class DonationAsset(db.Model):
    """Model for donated assets management"""
    __tablename__ = 'donation_assets'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # Thiết bị, Sách vở, Đồ dùng, etc.
    quantity = db.Column(db.Integer, default=1)
    estimated_value = db.Column(db.Numeric(12, 2))  # Estimated monetary value
    condition = db.Column(db.String(50))  # new, good, fair, poor
    
    # Donation info
    donor_name = db.Column(db.String(200))
    donor_phone = db.Column(db.String(20))
    donor_address = db.Column(db.Text)
    donation_date = db.Column(db.Date, nullable=False)
    
    # Distribution info
    status = db.Column(db.String(20), default='received')  # received, distributed, damaged, lost
    distributed_to = db.Column(db.String(200))  # Who received the asset
    distributed_date = db.Column(db.Date)
    distribution_notes = db.Column(db.Text)
    
    # Management
    location = db.Column(db.String(200))  # Where the asset is stored
    notes = db.Column(db.Text)
    
    # Foreign Keys
    received_by = db.Column(db.Integer, nullable=False)  # User who received the donation
    distributed_by = db.Column(db.Integer)  # User who distributed the asset
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def status_display(self):
        status_map = {
            'received': 'Đã nhận',
            'distributed': 'Đã phân phối',
            'damaged': 'Hư hỏng',
            'lost': 'Mất'
        }
        return status_map.get(self.status, self.status)
    
    @property
    def condition_display(self):
        condition_map = {
            'new': 'Mới',
            'good': 'Tốt',
            'fair': 'Khá',
            'poor': 'Kém'
        }
        return condition_map.get(self.condition, self.condition)
    
    @property
    def status_color(self):
        color_map = {
            'received': 'blue',
            'distributed': 'green',
            'damaged': 'red',
            'lost': 'gray'
        }
        return color_map.get(self.status, 'gray')
    
    def __repr__(self):
        return f'<DonationAsset {self.asset_name}: {self.status}>'

class DonationRecord(db.Model):
    """Model for donation giving/receiving records"""
    __tablename__ = 'donation_records'

    id = db.Column(db.Integer, primary_key=True)
    record_type = db.Column(db.String(20), nullable=False)  # 'received' or 'given'
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(12, 2))  # Monetary value if applicable

    # Donor/Recipient info
    donor_name = db.Column(db.String(200))
    donor_phone = db.Column(db.String(20))
    donor_address = db.Column(db.Text)
    recipient_name = db.Column(db.String(200))
    recipient_phone = db.Column(db.String(20))
    recipient_address = db.Column(db.Text)

    # Transaction details
    transaction_date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(100))  # Tiền mặt, Hiện vật, Học bổng, etc.
    purpose = db.Column(db.String(200))  # Mục đích quyên góp/trao tặng
    notes = db.Column(db.Text)

    # Management
    receipt_number = db.Column(db.String(50))
    status = db.Column(db.String(20), default='completed')  # pending, completed, cancelled

    # Foreign Keys
    created_by = db.Column(db.Integer, nullable=False)
    approved_by = db.Column(db.Integer)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def record_type_display(self):
        type_map = {
            'received': 'Nhận quyên góp',
            'given': 'Trao quyên góp'
        }
        return type_map.get(self.record_type, self.record_type)

    @property
    def status_display(self):
        status_map = {
            'pending': 'Chờ xử lý',
            'completed': 'Hoàn thành',
            'cancelled': 'Đã hủy'
        }
        return status_map.get(self.status, self.status or 'completed')

    @property
    def status_color(self):
        color_map = {
            'pending': 'yellow',
            'completed': 'green',
            'cancelled': 'red'
        }
        return color_map.get(self.status, 'gray')

    def __repr__(self):
        return f'<DonationRecord {self.record_type}: {self.title}>'
