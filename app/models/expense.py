from app import db
from datetime import datetime

class ExpenseCategory(db.Model):
    __tablename__ = 'expense_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#6B7280')  # Hex color
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    expenses = db.relationship('Expense', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<ExpenseCategory {self.name}>'

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    expense_date = db.Column(db.Date, nullable=False)
    receipt_number = db.Column(db.String(50))
    vendor = db.Column(db.String(200))
    payment_method = db.Column(db.String(50))  # cash, bank_transfer, card, etc.
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    notes = db.Column(db.Text)
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'), nullable=False)
    created_by = db.Column(db.Integer, nullable=False)
    approved_by = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    
    # Note: Relationships will be defined after User model is available
    
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
        return f'<Expense {self.title}: {self.amount}>'

class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'))
    created_by = db.Column(db.Integer, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Note: Relationships will be defined after User model is available
    
    @property
    def spent_amount(self):
        """Calculate total spent amount for this budget"""
        if self.category_id:
            expenses = Expense.query.filter(
                Expense.category_id == self.category_id,
                Expense.expense_date >= self.start_date,
                Expense.expense_date <= self.end_date,
                Expense.status == 'approved'
            ).all()
        else:
            expenses = Expense.query.filter(
                Expense.expense_date >= self.start_date,
                Expense.expense_date <= self.end_date,
                Expense.status == 'approved'
            ).all()
        
        return sum(expense.amount for expense in expenses)
    
    @property
    def remaining_amount(self):
        """Calculate remaining budget amount"""
        return self.total_amount - self.spent_amount
    
    @property
    def usage_percentage(self):
        """Calculate budget usage percentage"""
        if self.total_amount == 0:
            return 0
        return (self.spent_amount / self.total_amount) * 100
    
    def __repr__(self):
        return f'<Budget {self.name}: {self.total_amount}>'
