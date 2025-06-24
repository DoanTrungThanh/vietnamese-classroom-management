from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.class_model import Class
from app.models.student import Student
from app.models.schedule import Schedule
from app.forms.auth_forms import RegistrationForm
from app.forms.class_forms import ClassForm, StudentForm
from app.forms.schedule_forms import ScheduleForm
from app.forms.user_forms import CreateUserForm, EditUserForm, CreateClassForm, EditClassForm, CreateStudentForm, EditStudentForm
from werkzeug.security import generate_password_hash
from datetime import datetime

bp = Blueprint('admin', __name__)

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Bạn không có quyền truy cập trang này', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/users_tailwind.html', title='Quản lý người dùng', users=users)

@bp.route('/user/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                full_name=form.full_name.data,
                phone=form.phone.data,
                role=form.role.data,
                is_active=form.is_active.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash(f'Tạo người dùng {user.full_name} thành công!', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    return render_template('admin/create_user_tailwind.html', title='Thêm người dùng', form=form)

@bp.route('/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = EditUserForm(user)

    if form.validate_on_submit():
        try:
            user.username = form.username.data
            user.email = form.email.data
            user.full_name = form.full_name.data
            user.phone = form.phone.data
            user.role = form.role.data
            user.is_active = form.is_active.data

            # Update password if provided
            if form.password.data:
                user.set_password(form.password.data)

            db.session.commit()
            flash(f'Cập nhật người dùng {user.full_name} thành công!', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    # Pre-populate form
    if request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.full_name.data = user.full_name
        form.phone.data = user.phone
        form.role.data = user.role
        form.is_active.data = user.is_active

    return render_template('admin/edit_user_tailwind.html', title='Chỉnh sửa người dùng', form=form, user=user)

@bp.route('/user/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)

    # Prevent deleting current user
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Không thể xóa tài khoản của chính mình'})

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Xóa người dùng {user.full_name} thành công'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'})

@bp.route('/user/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(id):
    user = User.query.get_or_404(id)

    try:
        user.is_active = not user.is_active
        db.session.commit()
        status = 'kích hoạt' if user.is_active else 'vô hiệu hóa'
        return jsonify({'success': True, 'message': f'Đã {status} người dùng {user.full_name}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'})

@bp.route('/user/<int:id>/details')
@login_required
@admin_required
def user_details(id):
    user = User.query.get_or_404(id)

    role_display = {
        'admin': 'Quản trị viên',
        'manager': 'Quản sinh',
        'teacher': 'Giáo viên'
    }.get(user.role, user.role.title())

    return jsonify({
        'full_name': user.full_name,
        'username': user.username,
        'email': user.email,
        'phone': user.phone or 'Chưa cập nhật',
        'role_display': role_display,
        'is_active': user.is_active,
        'phone_display': user.phone or 'Chưa cập nhật',
        'created_at': user.created_at.strftime('%d/%m/%Y %H:%M') if user.created_at else 'Không có thông tin'
    })

@bp.route('/users/export')
@login_required
@admin_required
def export_users():
    try:
        from app.utils.excel_export import export_users_to_excel
        users = User.query.all()
        response = export_users_to_excel(users)
        if response:
            return response
        else:
            flash('Có lỗi xảy ra khi xuất file Excel', 'error')
            return redirect(url_for('admin.users'))
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        return redirect(url_for('admin.users'))

@bp.route('/classes/export')
@login_required
@admin_required
def export_classes():
    try:
        from app.utils.excel_export import export_classes_to_excel
        classes = Class.query.all()
        response = export_classes_to_excel(classes)
        if response:
            return response
        else:
            flash('Có lỗi xảy ra khi xuất file Excel', 'error')
            return redirect(url_for('admin.classes'))
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        return redirect(url_for('admin.classes'))



@bp.route('/classes')
@login_required
@admin_required
def classes():
    page = request.args.get('page', 1, type=int)
    classes = Class.query.filter_by(is_active=True).paginate(
        page=page, per_page=20, error_out=False)

    # Get unique block names for filter
    block_names = []
    return render_template('admin/classes_tailwind.html', title='Quản lý lớp học',
                         classes=classes.items if hasattr(classes, 'items') else classes, block_names=block_names)

@bp.route('/classes/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_class():
    form = ClassForm()
    if form.validate_on_submit():
        class_obj = Class(
            name=form.name.data,
            block_name=form.block_name.data,
            description=form.description.data,
            manager_id=form.manager_id.data if form.manager_id.data != 0 else None
        )
        db.session.add(class_obj)
        db.session.commit()
        flash('Tạo lớp học thành công!', 'success')
        return redirect(url_for('admin.classes'))
    return render_template('admin/create_class.html', title='Tạo lớp học', form=form)

@bp.route('/class/<int:class_id>/details')
@login_required
@admin_required
def class_details(class_id):
    from flask import jsonify

    class_obj = Class.query.get_or_404(class_id)

    return jsonify({
        'name': class_obj.name,
        'block_name': class_obj.block_name,
        'description': class_obj.description,
        'manager_name': class_obj.manager.full_name if class_obj.manager else None,
        'student_count': class_obj.student_count,
        'teachers': [{'id': t.id, 'full_name': t.full_name, 'phone': t.phone} for t in class_obj.teachers],
        'students': [{
            'student_code': s.student_code,
            'full_name': s.full_name,
            'parent_name': s.parent_name
        } for s in class_obj.students.filter_by(is_active=True).all()]
    })
