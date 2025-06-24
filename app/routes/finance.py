from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from app import db
from app.models.finance import Finance
from app.models.class_model import Class
from app.models.event import Event
from app.forms.finance_forms import FinanceForm

bp = Blueprint('finance', __name__)

def finance_required(f):
    """Decorator to check if user has finance access (admin or manager only)"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.is_teacher():
            flash('Bạn không có quyền truy cập chức năng tài chính', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/finance')
@login_required
@finance_required
def finance_dashboard():
    """Finance dashboard with summary statistics"""
    # Get date range from query params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = date.today().replace(day=1)  # First day of current month
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = date.today()
    
    # Base query
    query = Finance.query
    
    # Filter by manager's classes if not admin
    if current_user.is_manager():
        managed_class_ids = [c.id for c in Class.query.filter_by(manager_id=current_user.id, is_active=True)]
        query = query.filter(
            (Finance.class_id.in_(managed_class_ids)) | 
            (Finance.class_id.is_(None))
        )
    
    # Filter by date range
    query = query.filter(
        Finance.transaction_date >= start_date,
        Finance.transaction_date <= end_date
    )
    
    # Calculate statistics
    income_records = query.filter_by(type='income').all()
    expense_records = query.filter_by(type='expense').all()
    
    total_income = sum(r.amount for r in income_records)
    total_expense = sum(r.amount for r in expense_records)
    balance = total_income - total_expense
    
    # Recent transactions
    recent_transactions = query.order_by(Finance.created_at.desc()).limit(10).all()
    
    # Monthly summary for chart
    monthly_data = {}
    for record in query.all():
        month_key = record.transaction_date.strftime('%Y-%m')
        if month_key not in monthly_data:
            monthly_data[month_key] = {'income': 0, 'expense': 0}
        monthly_data[month_key][record.type] += record.amount
    
    return render_template('finance/dashboard.html',
                         title='Quản lý tài chính',
                         total_income=total_income,
                         total_expense=total_expense,
                         balance=balance,
                         income_count=len(income_records),
                         expense_count=len(expense_records),
                         recent_transactions=recent_transactions,
                         monthly_data=monthly_data,
                         start_date=start_date,
                         end_date=end_date)

@bp.route('/finance/transactions')
@login_required
@finance_required
def transactions():
    """List all transactions with filtering"""
    page = request.args.get('page', 1, type=int)
    transaction_type = request.args.get('type', '')
    category = request.args.get('category', '')
    class_id = request.args.get('class_id', type=int)
    
    # Base query
    query = Finance.query
    
    # Filter by manager's classes if not admin
    if current_user.is_manager():
        managed_class_ids = [c.id for c in Class.query.filter_by(manager_id=current_user.id, is_active=True)]
        query = query.filter(
            (Finance.class_id.in_(managed_class_ids)) | 
            (Finance.class_id.is_(None))
        )
    
    # Apply filters
    if transaction_type:
        query = query.filter_by(type=transaction_type)
    if category:
        query = query.filter(Finance.category.contains(category))
    if class_id:
        query = query.filter_by(class_id=class_id)
    
    # Paginate
    transactions = query.order_by(Finance.transaction_date.desc(), Finance.created_at.desc())\
                       .paginate(page=page, per_page=20, error_out=False)
    
    # Get filter options
    categories = db.session.query(Finance.category).distinct().filter(Finance.category.isnot(None)).all()
    categories = [c[0] for c in categories if c[0]]
    
    if current_user.is_admin():
        classes = Class.query.filter_by(is_active=True).all()
    else:
        classes = Class.query.filter_by(manager_id=current_user.id, is_active=True).all()
    
    return render_template('finance/transactions.html',
                         title='Danh sách giao dịch',
                         transactions=transactions,
                         categories=categories,
                         classes=classes,
                         current_type=transaction_type,
                         current_category=category,
                         current_class_id=class_id)

@bp.route('/finance/add', methods=['GET', 'POST'])
@login_required
@finance_required
def add_transaction():
    """Add new financial transaction"""
    form = FinanceForm()
    
    # Set choices based on user permissions
    if current_user.is_admin():
        form.class_id.choices = [(0, 'Không chọn')] + [
            (c.id, f"{c.name} - {c.block_name}") 
            for c in Class.query.filter_by(is_active=True).all()
        ]
    else:
        managed_classes = Class.query.filter_by(manager_id=current_user.id, is_active=True).all()
        form.class_id.choices = [(0, 'Không chọn')] + [
            (c.id, f"{c.name} - {c.block_name}") 
            for c in managed_classes
        ]
    
    form.event_id.choices = [(0, 'Không chọn')] + [
        (e.id, e.name) 
        for e in Event.query.filter_by(is_active=True).all()
    ]
    
    if form.validate_on_submit():
        transaction = Finance(
            type=form.type.data,
            amount=form.amount.data,
            description=form.description.data,
            category=form.category.data,
            class_id=form.class_id.data if form.class_id.data != 0 else None,
            event_id=form.event_id.data if form.event_id.data != 0 else None,
            creator_id=current_user.id,
            transaction_date=form.transaction_date.data
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Thêm phiếu {transaction.type_display.lower()} thành công!', 'success')
        return redirect(url_for('finance.transactions'))
    
    return render_template('finance/add_transaction.html',
                         title='Thêm giao dịch',
                         form=form)

@bp.route('/finance/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
@finance_required
def edit_transaction(transaction_id):
    """Edit existing transaction"""
    transaction = Finance.query.get_or_404(transaction_id)
    
    # Check permissions
    if current_user.is_manager():
        if transaction.class_id:
            class_obj = Class.query.get(transaction.class_id)
            if not class_obj or class_obj.manager_id != current_user.id:
                flash('Bạn không có quyền chỉnh sửa giao dịch này', 'error')
                return redirect(url_for('finance.transactions'))
    
    form = FinanceForm(obj=transaction)
    
    # Set choices
    if current_user.is_admin():
        form.class_id.choices = [(0, 'Không chọn')] + [
            (c.id, f"{c.name} - {c.block_name}") 
            for c in Class.query.filter_by(is_active=True).all()
        ]
    else:
        managed_classes = Class.query.filter_by(manager_id=current_user.id, is_active=True).all()
        form.class_id.choices = [(0, 'Không chọn')] + [
            (c.id, f"{c.name} - {c.block_name}") 
            for c in managed_classes
        ]
    
    form.event_id.choices = [(0, 'Không chọn')] + [
        (e.id, e.name) 
        for e in Event.query.filter_by(is_active=True).all()
    ]
    
    # Set current values
    if transaction.class_id:
        form.class_id.data = transaction.class_id
    else:
        form.class_id.data = 0
        
    if transaction.event_id:
        form.event_id.data = transaction.event_id
    else:
        form.event_id.data = 0
    
    if form.validate_on_submit():
        transaction.type = form.type.data
        transaction.amount = form.amount.data
        transaction.description = form.description.data
        transaction.category = form.category.data
        transaction.class_id = form.class_id.data if form.class_id.data != 0 else None
        transaction.event_id = form.event_id.data if form.event_id.data != 0 else None
        transaction.transaction_date = form.transaction_date.data
        
        db.session.commit()
        flash('Cập nhật giao dịch thành công!', 'success')
        return redirect(url_for('finance.transactions'))
    
    return render_template('finance/edit_transaction.html',
                         title='Chỉnh sửa giao dịch',
                         form=form,
                         transaction=transaction)

@bp.route('/finance/delete/<int:transaction_id>', methods=['POST'])
@login_required
@finance_required
def delete_transaction(transaction_id):
    """Delete transaction"""
    transaction = Finance.query.get_or_404(transaction_id)
    
    # Check permissions
    if current_user.is_manager():
        if transaction.class_id:
            class_obj = Class.query.get(transaction.class_id)
            if not class_obj or class_obj.manager_id != current_user.id:
                flash('Bạn không có quyền xóa giao dịch này', 'error')
                return redirect(url_for('finance.transactions'))
    
    db.session.delete(transaction)
    db.session.commit()
    flash('Xóa giao dịch thành công!', 'success')
    return redirect(url_for('finance.transactions'))

@bp.route('/finance/report')
@login_required
@finance_required
def financial_report():
    """Generate financial reports"""
    # Get date range
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = date.today().replace(day=1)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = date.today()
    
    # Base query
    query = Finance.query.filter(
        Finance.transaction_date >= start_date,
        Finance.transaction_date <= end_date
    )
    
    # Filter by manager's classes if not admin
    if current_user.is_manager():
        managed_class_ids = [c.id for c in Class.query.filter_by(manager_id=current_user.id, is_active=True)]
        query = query.filter(
            (Finance.class_id.in_(managed_class_ids)) | 
            (Finance.class_id.is_(None))
        )
    
    transactions = query.all()
    
    # Generate report data
    report_data = {
        'summary': {
            'total_income': sum(t.amount for t in transactions if t.type == 'income'),
            'total_expense': sum(t.amount for t in transactions if t.type == 'expense'),
            'transaction_count': len(transactions)
        },
        'by_category': {},
        'by_class': {},
        'by_month': {}
    }
    
    # Group by category
    for transaction in transactions:
        category = transaction.category or 'Khác'
        if category not in report_data['by_category']:
            report_data['by_category'][category] = {'income': 0, 'expense': 0}
        report_data['by_category'][category][transaction.type] += transaction.amount
    
    # Group by class
    for transaction in transactions:
        class_name = transaction.related_class.name if transaction.related_class else 'Chung'
        if class_name not in report_data['by_class']:
            report_data['by_class'][class_name] = {'income': 0, 'expense': 0}
        report_data['by_class'][class_name][transaction.type] += transaction.amount
    
    # Group by month
    for transaction in transactions:
        month_key = transaction.transaction_date.strftime('%Y-%m')
        if month_key not in report_data['by_month']:
            report_data['by_month'][month_key] = {'income': 0, 'expense': 0}
        report_data['by_month'][month_key][transaction.type] += transaction.amount
    
    report_data['summary']['balance'] = report_data['summary']['total_income'] - report_data['summary']['total_expense']
    
    return render_template('finance/report.html',
                         title='Báo cáo tài chính',
                         report_data=report_data,
                         start_date=start_date,
                         end_date=end_date)
