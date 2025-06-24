from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.expense import Expense, ExpenseCategory, Budget
from app.forms.expense_forms import ExpenseForm, ExpenseCategoryForm, BudgetForm, ExpenseApprovalForm, ExpenseFilterForm
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from functools import wraps

bp = Blueprint('expense', __name__, url_prefix='/expense')

def admin_or_manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_admin() or current_user.is_manager()):
            flash('Bạn không có quyền truy cập trang này.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_or_manager_required
def dashboard():
    # Get current month statistics
    current_month = date.today().replace(day=1)
    next_month = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1)
    
    # Monthly expenses
    monthly_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.expense_date >= current_month,
        Expense.expense_date < next_month,
        Expense.status == 'approved'
    ).scalar() or 0
    
    # Pending expenses count
    pending_count = Expense.query.filter_by(status='pending').count()
    
    # Total categories
    categories_count = ExpenseCategory.query.filter_by(is_active=True).count()
    
    # Active budgets
    active_budgets = Budget.query.filter(
        Budget.is_active == True,
        Budget.start_date <= date.today(),
        Budget.end_date >= date.today()
    ).all()
    
    # Recent expenses
    recent_expenses = Expense.query.order_by(Expense.created_at.desc()).limit(10).all()
    
    # Expenses by category (current month)
    category_stats = db.session.query(
        ExpenseCategory.name,
        ExpenseCategory.color,
        func.sum(Expense.amount).label('total')
    ).join(Expense).filter(
        Expense.expense_date >= current_month,
        Expense.expense_date < next_month,
        Expense.status == 'approved'
    ).group_by(ExpenseCategory.id).all()
    
    return render_template('expense/dashboard_tailwind.html',
                         title='Quản lý chi tiêu',
                         monthly_expenses=monthly_expenses,
                         pending_count=pending_count,
                         categories_count=categories_count,
                         active_budgets=active_budgets,
                         recent_expenses=recent_expenses,
                         category_stats=category_stats)

@bp.route('/expenses')
@login_required
@admin_or_manager_required
def expenses():
    page = request.args.get('page', 1, type=int)
    filter_form = ExpenseFilterForm()
    
    # Build query
    query = Expense.query
    
    # Apply filters
    if request.args.get('start_date'):
        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        query = query.filter(Expense.expense_date >= start_date)
    
    if request.args.get('end_date'):
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        query = query.filter(Expense.expense_date <= end_date)
    
    if request.args.get('category_id', type=int):
        query = query.filter(Expense.category_id == request.args.get('category_id', type=int))
    
    if request.args.get('status'):
        query = query.filter(Expense.status == request.args.get('status'))
    
    if request.args.get('payment_method'):
        query = query.filter(Expense.payment_method == request.args.get('payment_method'))
    
    # Search
    search = request.args.get('search', '')
    if search:
        query = query.filter(or_(
            Expense.title.contains(search),
            Expense.description.contains(search),
            Expense.vendor.contains(search)
        ))
    
    expenses = query.order_by(Expense.expense_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('expense/expenses_tailwind.html',
                         title='Danh sách chi tiêu',
                         expenses=expenses,
                         filter_form=filter_form,
                         search=search)

@bp.route('/expense/create', methods=['GET', 'POST'])
@login_required
@admin_or_manager_required
def create_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        try:
            expense = Expense(
                title=form.title.data,
                description=form.description.data,
                amount=form.amount.data,
                expense_date=form.expense_date.data,
                category_id=form.category_id.data,
                receipt_number=form.receipt_number.data,
                vendor=form.vendor.data,
                payment_method=form.payment_method.data,
                notes=form.notes.data,
                created_by=current_user.id,
                status='pending' if not current_user.is_admin() else 'approved'
            )
            
            if current_user.is_admin():
                expense.approved_by = current_user.id
                expense.approved_at = datetime.utcnow()
            
            db.session.add(expense)
            db.session.commit()
            flash('Tạo chi tiêu thành công!', 'success')
            return redirect(url_for('expense.expenses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
    
    return render_template('expense/create_expense_tailwind.html', title='Thêm chi tiêu', form=form)

@bp.route('/expense/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_or_manager_required
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    
    # Check permissions
    if not current_user.is_admin() and expense.created_by != current_user.id:
        flash('Bạn không có quyền chỉnh sửa chi tiêu này.', 'error')
        return redirect(url_for('expense.expenses'))
    
    form = ExpenseForm(obj=expense)
    if form.validate_on_submit():
        try:
            expense.title = form.title.data
            expense.description = form.description.data
            expense.amount = form.amount.data
            expense.expense_date = form.expense_date.data
            expense.category_id = form.category_id.data
            expense.receipt_number = form.receipt_number.data
            expense.vendor = form.vendor.data
            expense.payment_method = form.payment_method.data
            expense.notes = form.notes.data
            expense.updated_at = datetime.utcnow()
            
            # Reset approval if edited
            if expense.status == 'approved' and not current_user.is_admin():
                expense.status = 'pending'
                expense.approved_by = None
                expense.approved_at = None
            
            db.session.commit()
            flash('Cập nhật chi tiêu thành công!', 'success')
            return redirect(url_for('expense.expenses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
    
    return render_template('expense/edit_expense_tailwind.html', title='Chỉnh sửa chi tiêu', form=form, expense=expense)

@bp.route('/expense/<int:id>/delete', methods=['POST'])
@login_required
@admin_or_manager_required
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    
    # Check permissions
    if not current_user.is_admin() and expense.created_by != current_user.id:
        return jsonify({'success': False, 'message': 'Bạn không có quyền xóa chi tiêu này'})
    
    try:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Xóa chi tiêu thành công'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'})

@bp.route('/expense/<int:id>/approve', methods=['POST'])
@login_required
@admin_or_manager_required
def approve_expense(id):
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Chỉ admin mới có quyền duyệt chi tiêu'})
    
    expense = Expense.query.get_or_404(id)
    form = ExpenseApprovalForm()
    
    if form.validate_on_submit():
        try:
            expense.status = form.status.data
            expense.approved_by = current_user.id
            expense.approved_at = datetime.utcnow()
            if form.notes.data:
                expense.notes = (expense.notes or '') + f'\n[Duyệt] {form.notes.data}'
            
            db.session.commit()
            status_text = 'duyệt' if form.status.data == 'approved' else 'từ chối'
            return jsonify({'success': True, 'message': f'Đã {status_text} chi tiêu'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'})
    
    return jsonify({'success': False, 'message': 'Dữ liệu không hợp lệ'})

@bp.route('/categories')
@login_required
@admin_or_manager_required
def categories():
    categories = ExpenseCategory.query.order_by(ExpenseCategory.name).all()
    return render_template('expense/categories_tailwind.html', title='Danh mục chi tiêu', categories=categories)

@bp.route('/category/create', methods=['GET', 'POST'])
@login_required
@admin_or_manager_required
def create_category():
    form = ExpenseCategoryForm()
    if form.validate_on_submit():
        try:
            category = ExpenseCategory(
                name=form.name.data,
                description=form.description.data,
                color=form.color.data or '#6B7280'
            )
            db.session.add(category)
            db.session.commit()
            flash('Tạo danh mục thành công!', 'success')
            return redirect(url_for('expense.categories'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
    
    return render_template('expense/create_category_tailwind.html', title='Thêm danh mục', form=form)

@bp.route('/budgets')
@login_required
@admin_or_manager_required
def budgets():
    budgets = Budget.query.order_by(Budget.start_date.desc()).all()
    return render_template('expense/budgets_tailwind.html', title='Quản lý ngân sách', budgets=budgets)

@bp.route('/budget/create', methods=['GET', 'POST'])
@login_required
@admin_or_manager_required
def create_budget():
    form = BudgetForm()
    if form.validate_on_submit():
        try:
            budget = Budget(
                name=form.name.data,
                description=form.description.data,
                total_amount=form.total_amount.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                category_id=form.category_id.data if form.category_id.data != 0 else None,
                created_by=current_user.id
            )
            db.session.add(budget)
            db.session.commit()
            flash('Tạo ngân sách thành công!', 'success')
            return redirect(url_for('expense.budgets'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
    
    return render_template('expense/create_budget_tailwind.html', title='Thêm ngân sách', form=form)

@bp.route('/expenses/export')
@login_required
@admin_or_manager_required
def export_expenses():
    try:
        from app.utils.excel_export import export_expenses_to_excel
        expenses = Expense.query.all()
        response = export_expenses_to_excel(expenses)
        if response:
            return response
        else:
            flash('Có lỗi xảy ra khi xuất file Excel', 'error')
            return redirect(url_for('expense.expenses'))
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        return redirect(url_for('expense.expenses'))
