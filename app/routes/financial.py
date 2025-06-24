from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.financial_transaction import FinancialTransaction, DonationAsset, DonationRecord
from app.forms.financial_forms import (FinancialTransactionForm, DonationAssetForm,
                                     AssetDistributionForm, AssetStatusUpdateForm, FinancialReportForm, DonationRecordForm)
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from functools import wraps

bp = Blueprint('financial', __name__, url_prefix='/financial')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Bạn không có quyền truy cập trang này.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def dashboard():
    """Financial dashboard with income/expense overview"""
    # Get current month statistics
    current_month = date.today().replace(day=1)
    next_month = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1)
    
    # Monthly income and expenses
    monthly_income = db.session.query(func.sum(FinancialTransaction.amount)).filter(
        FinancialTransaction.transaction_date >= current_month,
        FinancialTransaction.transaction_date < next_month,
        FinancialTransaction.transaction_type == 'income',
        FinancialTransaction.status == 'approved'
    ).scalar() or 0
    
    monthly_expense = db.session.query(func.sum(FinancialTransaction.amount)).filter(
        FinancialTransaction.transaction_date >= current_month,
        FinancialTransaction.transaction_date < next_month,
        FinancialTransaction.transaction_type == 'expense',
        FinancialTransaction.status == 'approved'
    ).scalar() or 0
    
    # Net income
    net_income = monthly_income - monthly_expense
    
    # Donation assets statistics
    total_assets = DonationAsset.query.count()
    distributed_assets = DonationAsset.query.filter_by(status='distributed').count()
    available_assets = DonationAsset.query.filter_by(status='received').count()

    # Donation expense (chi quyên góp) statistics
    donation_expense = db.session.query(func.sum(FinancialTransaction.amount)).filter(
        FinancialTransaction.transaction_date >= current_month,
        FinancialTransaction.transaction_date < next_month,
        FinancialTransaction.transaction_type == 'expense',
        FinancialTransaction.category == 'donation',
        FinancialTransaction.status == 'approved'
    ).scalar() or 0
    
    # Recent transactions
    recent_transactions = FinancialTransaction.query.order_by(
        FinancialTransaction.transaction_date.desc()
    ).limit(10).all()
    
    # Recent donations
    recent_donations = DonationAsset.query.order_by(
        DonationAsset.donation_date.desc()
    ).limit(5).all()
    
    # Income by category (current month)
    income_stats = db.session.query(
        FinancialTransaction.category,
        func.sum(FinancialTransaction.amount).label('total')
    ).filter(
        FinancialTransaction.transaction_date >= current_month,
        FinancialTransaction.transaction_date < next_month,
        FinancialTransaction.transaction_type == 'income',
        FinancialTransaction.status == 'approved'
    ).group_by(FinancialTransaction.category).all()
    
    # Expense by category (current month)
    expense_stats = db.session.query(
        FinancialTransaction.category,
        func.sum(FinancialTransaction.amount).label('total')
    ).filter(
        FinancialTransaction.transaction_date >= current_month,
        FinancialTransaction.transaction_date < next_month,
        FinancialTransaction.transaction_type == 'expense',
        FinancialTransaction.status == 'approved'
    ).group_by(FinancialTransaction.category).all()
    
    return render_template('financial/dashboard_tailwind.html',
                         title='Quản lý tài chính',
                         monthly_income=monthly_income,
                         monthly_expense=monthly_expense,
                         net_income=net_income,
                         total_assets=total_assets,
                         distributed_assets=distributed_assets,
                         available_assets=available_assets,
                         donation_expense=donation_expense,
                         recent_transactions=recent_transactions,
                         recent_donations=recent_donations,
                         income_stats=income_stats,
                         expense_stats=expense_stats)

@bp.route('/transactions')
@login_required
@admin_required
def transactions():
    """List all financial transactions"""
    page = request.args.get('page', 1, type=int)
    
    # Build query
    query = FinancialTransaction.query
    
    # Apply filters
    if request.args.get('start_date'):
        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        query = query.filter(FinancialTransaction.transaction_date >= start_date)
    
    if request.args.get('end_date'):
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        query = query.filter(FinancialTransaction.transaction_date <= end_date)
    
    if request.args.get('transaction_type'):
        query = query.filter(FinancialTransaction.transaction_type == request.args.get('transaction_type'))
    
    if request.args.get('category'):
        query = query.filter(FinancialTransaction.category == request.args.get('category'))
    
    # Search
    search = request.args.get('search', '')
    if search:
        query = query.filter(or_(
            FinancialTransaction.title.contains(search),
            FinancialTransaction.description.contains(search),
            FinancialTransaction.vendor_payer.contains(search)
        ))
    
    transactions = query.order_by(FinancialTransaction.transaction_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('financial/transactions_tailwind.html',
                         title='Quản lý thu chi',
                         transactions=transactions,
                         search=search)

@bp.route('/transaction/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_transaction():
    """Create new financial transaction"""
    form = FinancialTransactionForm()
    if form.validate_on_submit():
        try:
            transaction = FinancialTransaction(
                title=form.title.data,
                description=form.description.data,
                amount=form.amount.data,
                transaction_date=form.transaction_date.data,
                transaction_type=form.transaction_type.data,
                category=form.category.data,
                payment_method=form.payment_method.data,
                receipt_number=form.receipt_number.data,
                vendor_payer=form.vendor_payer.data,
                notes=form.notes.data,
                created_by=current_user.id,
                status='approved',  # Admin creates approved transactions
                approved_by=current_user.id,
                approved_at=datetime.utcnow()
            )
            
            db.session.add(transaction)
            db.session.commit()
            flash('Tạo giao dịch thành công!', 'success')
            return redirect(url_for('financial.transactions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
    
    return render_template('financial/create_transaction_tailwind.html',
                         title='Thêm giao dịch', form=form)

@bp.route('/donations')
@login_required
@admin_required
def donations():
    """List all donation assets"""
    page = request.args.get('page', 1, type=int)

    # Build query
    query = DonationAsset.query

    # Apply filters
    if request.args.get('status'):
        query = query.filter(DonationAsset.status == request.args.get('status'))

    if request.args.get('category'):
        query = query.filter(DonationAsset.category == request.args.get('category'))

    # Search
    search = request.args.get('search', '')
    if search:
        query = query.filter(or_(
            DonationAsset.asset_name.contains(search),
            DonationAsset.description.contains(search),
            DonationAsset.donor_name.contains(search)
        ))

    donations = query.order_by(DonationAsset.donation_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('financial/donations_tailwind.html',
                         title='Quản lý tài sản quyên góp',
                         donations=donations,
                         search=search)

@bp.route('/donation/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_donation():
    """Create new donation asset record"""
    form = DonationAssetForm()
    if form.validate_on_submit():
        try:
            donation = DonationAsset(
                asset_name=form.asset_name.data,
                description=form.description.data,
                category=form.category.data,
                quantity=form.quantity.data,
                estimated_value=form.estimated_value.data,
                condition=form.condition.data,
                donor_name=form.donor_name.data,
                donor_phone=form.donor_phone.data,
                donor_address=form.donor_address.data,
                donation_date=form.donation_date.data,
                location=form.location.data,
                notes=form.notes.data,
                received_by=current_user.id,
                status='received'
            )

            db.session.add(donation)
            db.session.commit()
            flash('Ghi nhận tài sản quyên góp thành công!', 'success')
            return redirect(url_for('financial.donations'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    return render_template('financial/create_donation_tailwind.html',
                         title='Nhận tài sản quyên góp', form=form)

@bp.route('/donation/<int:id>/distribute', methods=['GET', 'POST'])
@login_required
@admin_required
def distribute_donation(id):
    """Distribute donation asset"""
    donation = DonationAsset.query.get_or_404(id)

    if donation.status != 'received':
        flash('Chỉ có thể phân phối tài sản đã nhận', 'error')
        return redirect(url_for('financial.donations'))

    form = AssetDistributionForm()
    if form.validate_on_submit():
        try:
            donation.status = 'distributed'
            donation.distributed_to = form.distributed_to.data
            donation.distributed_date = form.distributed_date.data
            donation.distribution_notes = form.distribution_notes.data
            donation.distributed_by = current_user.id
            donation.updated_at = datetime.utcnow()

            # Create expense transaction for asset distribution
            if donation.estimated_value and donation.estimated_value > 0:
                expense_transaction = FinancialTransaction(
                    title=f'Chi phân phối: {donation.asset_name}',
                    description=f'Phân phối tài sản quyên góp cho {form.distributed_to.data}',
                    amount=donation.estimated_value,
                    transaction_date=form.distributed_date.data,
                    transaction_type='expense',
                    category='donation',
                    payment_method='other',
                    vendor_payer=form.distributed_to.data,
                    notes=f'Phân phối tài sản ID: {donation.id}. {form.distribution_notes.data or ""}',
                    created_by=current_user.id,
                    status='approved',
                    approved_by=current_user.id,
                    approved_at=datetime.utcnow()
                )
                db.session.add(expense_transaction)

            db.session.commit()
            flash('Phân phối tài sản thành công!', 'success')
            return redirect(url_for('financial.donations'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    return render_template('financial/distribute_donation_tailwind.html',
                         title='Phân phối tài sản', form=form, donation=donation)

@bp.route('/donation/<int:id>/update_status', methods=['POST'])
@login_required
@admin_required
def update_donation_status(id):
    """Update donation asset status"""
    donation = DonationAsset.query.get_or_404(id)
    form = AssetStatusUpdateForm()

    if form.validate_on_submit():
        try:
            donation.status = form.status.data
            if form.notes.data:
                donation.notes = (donation.notes or '') + f'\n[{datetime.now().strftime("%Y-%m-%d")}] {form.notes.data}'
            donation.updated_at = datetime.utcnow()

            db.session.commit()
            return jsonify({'success': True, 'message': 'Cập nhật trạng thái thành công'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'})

    return jsonify({'success': False, 'message': 'Dữ liệu không hợp lệ'})

@bp.route('/donation/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_donation(id):
    """Delete donation asset"""
    donation = DonationAsset.query.get_or_404(id)

    try:
        db.session.delete(donation)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Xóa tài sản quyên góp thành công'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'})

@bp.route('/transaction/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_transaction(id):
    """Delete financial transaction"""
    transaction = FinancialTransaction.query.get_or_404(id)

    try:
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Xóa giao dịch thành công'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'})

@bp.route('/reports')
@login_required
@admin_required
def reports():
    """Financial reports"""
    form = FinancialReportForm()

    # Default to current month
    current_month = date.today().replace(day=1)
    form.start_date.data = current_month
    form.end_date.data = date.today()

    return render_template('financial/reports_tailwind.html',
                         title='Báo cáo tài chính', form=form)

@bp.route('/donation-records')
@login_required
@admin_required
def donation_records():
    """List all donation records"""
    page = request.args.get('page', 1, type=int)

    # Build query
    query = DonationRecord.query

    # Apply filters
    if request.args.get('record_type'):
        query = query.filter(DonationRecord.record_type == request.args.get('record_type'))

    if request.args.get('category'):
        query = query.filter(DonationRecord.category == request.args.get('category'))

    # Search
    search = request.args.get('search', '')
    if search:
        query = query.filter(or_(
            DonationRecord.title.contains(search),
            DonationRecord.description.contains(search),
            DonationRecord.donor_name.contains(search),
            DonationRecord.recipient_name.contains(search)
        ))

    records = query.order_by(DonationRecord.transaction_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('financial/donation_records_tailwind.html',
                         title='Bản ghi quyên góp',
                         records=records,
                         search=search)

@bp.route('/donation-record/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_donation_record():
    """Create new donation record"""
    form = DonationRecordForm()
    if form.validate_on_submit():
        try:
            record = DonationRecord(
                record_type=form.record_type.data,
                title=form.title.data,
                description=form.description.data,
                amount=form.amount.data,
                transaction_date=form.transaction_date.data,
                category=form.category.data,
                purpose=form.purpose.data,
                donor_name=form.donor_name.data,
                donor_phone=form.donor_phone.data,
                donor_address=form.donor_address.data,
                recipient_name=form.recipient_name.data,
                recipient_phone=form.recipient_phone.data,
                recipient_address=form.recipient_address.data,
                receipt_number=form.receipt_number.data,
                notes=form.notes.data,
                created_by=current_user.id,
                status='completed'
            )

            db.session.add(record)

            # Create corresponding financial transaction if amount is specified
            if record.amount and record.amount > 0:
                transaction_type = 'income' if record.record_type == 'received' else 'expense'
                transaction = FinancialTransaction(
                    title=f'{record.record_type_display}: {record.title}',
                    description=record.description,
                    amount=record.amount,
                    transaction_date=record.transaction_date,
                    transaction_type=transaction_type,
                    category='donation',
                    payment_method='other',
                    vendor_payer=record.donor_name if record.record_type == 'received' else record.recipient_name,
                    notes=f'Bản ghi quyên góp ID: {record.id}. {record.notes or ""}',
                    created_by=current_user.id,
                    status='approved',
                    approved_by=current_user.id,
                    approved_at=datetime.utcnow()
                )
                db.session.add(transaction)

            db.session.commit()
            flash('Tạo bản ghi quyên góp thành công!', 'success')
            return redirect(url_for('financial.donation_records'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    return render_template('financial/create_donation_record_tailwind.html',
                         title='Tạo bản ghi quyên góp', form=form)

@bp.route('/transactions/export')
@login_required
@admin_or_manager_required
def export_transactions():
    """Export financial transactions to Excel"""
    try:
        from app.utils.excel_export import export_financial_transactions_to_excel

        # Get filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        transaction_type = request.args.get('type')

        # Build query
        query = Finance.query

        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Finance.transaction_date >= start_date)

        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Finance.transaction_date <= end_date)

        if transaction_type and transaction_type != 'all':
            query = query.filter(Finance.type == transaction_type)

        # Filter by manager's classes if not admin
        if current_user.is_manager():
            managed_class_ids = [c.id for c in Class.query.filter_by(manager_id=current_user.id, is_active=True)]
            query = query.filter(
                (Finance.class_id.in_(managed_class_ids)) |
                (Finance.class_id.is_(None))
            )

        transactions = query.order_by(Finance.transaction_date.desc()).all()

        response = export_financial_transactions_to_excel(transactions)
        if response:
            return response
        else:
            flash('Có lỗi xảy ra khi xuất file Excel', 'error')
            return redirect(url_for('financial.transactions'))

    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        return redirect(url_for('financial.transactions'))

@bp.route('/donations/export')
@login_required
@admin_or_manager_required
def export_donations():
    """Export donations to Excel"""
    try:
        from app.utils.excel_export import export_donations_to_excel

        # Get filter parameters
        status = request.args.get('status')

        # Build query
        query = Donation.query

        if status and status != 'all':
            query = query.filter(Donation.status == status)

        donations = query.order_by(Donation.donation_date.desc()).all()

        response = export_donations_to_excel(donations)
        if response:
            return response
        else:
            flash('Có lỗi xảy ra khi xuất file Excel', 'error')
            return redirect(url_for('financial.donations'))

    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        return redirect(url_for('financial.donations'))
