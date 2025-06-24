import io
import pandas as pd
from flask import make_response
from datetime import datetime

def create_excel_response(data, filename, sheet_name='Sheet1'):
    """
    Create Excel file response from data
    """
    try:
        # Create Excel file in memory
        output = io.BytesIO()
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Write to Excel
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        output.seek(0)
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        print(f"Error creating Excel file: {str(e)}")
        return None

def export_users_to_excel(users):
    """
    Export users data to Excel
    """
    data = []
    for user in users:
        data.append({
            'ID': user.id,
            'Họ và tên': user.full_name,
            'Tên đăng nhập': user.username,
            'Email': user.email,
            'Số điện thoại': user.phone or '',
            'Vai trò': {
                'admin': 'Quản trị viên',
                'manager': 'Quản sinh',
                'teacher': 'Giáo viên'
            }.get(user.role, user.role),
            'Trạng thái': 'Hoạt động' if user.is_active else 'Không hoạt động',
            'Ngày tạo': user.created_at.strftime('%d/%m/%Y %H:%M') if user.created_at else '',
            'Địa chỉ': user.address or ''
        })
    
    filename = f'danh_sach_nguoi_dung_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return create_excel_response(data, filename, 'Danh sách người dùng')

def export_classes_to_excel(classes):
    """
    Export classes data to Excel
    """
    data = []
    for class_obj in classes:
        data.append({
            'ID': class_obj.id,
            'Tên lớp': class_obj.name,
            'Mô tả': class_obj.description or '',
            'Quản sinh': class_obj.manager.full_name if class_obj.manager else '',
            'Sĩ số hiện tại': class_obj.student_count,
            'Sĩ số tối đa': class_obj.max_students or '',
            'Trạng thái': 'Hoạt động' if class_obj.is_active else 'Không hoạt động',
            'Ngày tạo': class_obj.created_at.strftime('%d/%m/%Y %H:%M') if class_obj.created_at else ''
        })
    
    filename = f'danh_sach_lop_hoc_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return create_excel_response(data, filename, 'Danh sách lớp học')

def export_students_to_excel(students):
    """
    Export students data to Excel
    """
    data = []
    for student in students:
        data.append({
            'ID': student.id,
            'Họ và tên': student.full_name,
            'Mã học sinh': student.student_id or '',
            'Lớp học': student.class_obj.name if student.class_obj else '',
            'Ngày sinh': student.date_of_birth.strftime('%d/%m/%Y') if student.date_of_birth else '',
            'Tên phụ huynh': student.parent_name or '',
            'SĐT phụ huynh': student.parent_phone or '',
            'Địa chỉ': student.address or '',
            'Trạng thái': 'Đang học' if student.is_active else 'Đã nghỉ',
            'Ngày nhập học': student.enrollment_date.strftime('%d/%m/%Y') if student.enrollment_date else ''
        })
    
    filename = f'danh_sach_hoc_sinh_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return create_excel_response(data, filename, 'Danh sách học sinh')

def export_expenses_to_excel(expenses):
    """
    Export expenses data to Excel
    """
    data = []
    for expense in expenses:
        data.append({
            'ID': expense.id,
            'Tiêu đề': expense.title,
            'Mô tả': expense.description or '',
            'Số tiền': float(expense.amount),
            'Ngày chi tiêu': expense.expense_date.strftime('%d/%m/%Y'),
            'Danh mục': expense.category.name,
            'Nhà cung cấp': expense.vendor or '',
            'Số hóa đơn': expense.receipt_number or '',
            'Phương thức thanh toán': expense.payment_method_display,
            'Trạng thái': expense.status_display,
            'Người tạo': expense.creator.full_name if expense.creator else '',
            'Người duyệt': expense.approver.full_name if expense.approver else '',
            'Ngày tạo': expense.created_at.strftime('%d/%m/%Y %H:%M') if expense.created_at else '',
            'Ghi chú': expense.notes or ''
        })
    
    filename = f'danh_sach_chi_tieu_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return create_excel_response(data, filename, 'Danh sách chi tiêu')

def export_attendance_to_excel(attendance_records, class_name=None, date_range=None):
    """
    Export attendance data to Excel
    """
    data = []
    for record in attendance_records:
        data.append({
            'ID': record.id,
            'Học sinh': record.student.full_name,
            'Lớp': record.schedule.class_obj.name,
            'Giáo viên': record.schedule.teacher.full_name,
            'Ngày': record.date.strftime('%d/%m/%Y'),
            'Khung giờ': record.schedule.time_slot.name,
            'Thời gian': f"{record.schedule.time_slot.start_time.strftime('%H:%M')} - {record.schedule.time_slot.end_time.strftime('%H:%M')}",
            'Trạng thái': {
                'present': 'Có mặt',
                'absent_without_reason': 'Vắng không phép',
                'absent_with_reason': 'Vắng có phép'
            }.get(record.status, record.status),
            'Ghi chú': record.notes or ''
        })
    
    # Create filename with class and date info
    filename_parts = ['diem_danh']
    if class_name:
        filename_parts.append(class_name.replace(' ', '_'))
    if date_range:
        filename_parts.append(date_range.replace('/', ''))
    filename_parts.append(datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    filename = f'{"_".join(filename_parts)}.xlsx'
    return create_excel_response(data, filename, 'Điểm danh')

def export_schedule_to_excel(schedules):
    """
    Export schedule data to Excel
    """
    data = []
    for schedule in schedules:
        data.append({
            'ID': schedule.id,
            'Giáo viên': schedule.teacher.full_name,
            'Lớp học': schedule.class_obj.name,
            'Khung giờ': schedule.time_slot.name,
            'Thời gian': f"{schedule.time_slot.start_time.strftime('%H:%M')} - {schedule.time_slot.end_time.strftime('%H:%M')}",
            'Thứ': {
                0: 'Chủ nhật',
                1: 'Thứ 2',
                2: 'Thứ 3', 
                3: 'Thứ 4',
                4: 'Thứ 5',
                5: 'Thứ 6',
                6: 'Thứ 7'
            }.get(schedule.day_of_week, f'Thứ {schedule.day_of_week}'),
            'Trạng thái': 'Hoạt động' if schedule.is_active else 'Tạm dừng',
            'Ngày tạo': schedule.created_at.strftime('%d/%m/%Y %H:%M') if schedule.created_at else ''
        })
    
    filename = f'lich_day_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return create_excel_response(data, filename, 'Lịch dạy')

def export_time_slots_to_excel(time_slots):
    """
    Export time slots data to Excel
    """
    data = []
    for slot in time_slots:
        data.append({
            'ID': slot.id,
            'Tên khung giờ': slot.name,
            'Thời gian bắt đầu': slot.start_time.strftime('%H:%M'),
            'Thời gian kết thúc': slot.end_time.strftime('%H:%M'),
            'Buổi': slot.session,
            'Mô tả': slot.description or '',
            'Trạng thái': 'Hoạt động' if slot.is_active else 'Không hoạt động',
            'Ngày tạo': slot.created_at.strftime('%d/%m/%Y %H:%M') if slot.created_at else ''
        })
    
    filename = f'khung_gio_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return create_excel_response(data, filename, 'Khung giờ')
