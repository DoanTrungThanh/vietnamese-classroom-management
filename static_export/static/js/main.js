// Main JavaScript file for the classroom management system

// Notification System
class NotificationSystem {
    constructor() {
        this.container = this.createContainer();
        document.body.appendChild(this.container);
    }

    createContainer() {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        return container;
    }

    show(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification-popup`;
        notification.style.cssText = `
            margin-bottom: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border: none;
            border-radius: 8px;
            animation: slideInRight 0.3s ease-out;
        `;

        const icon = this.getIcon(type);
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="${icon} me-2"></i>
                <span>${message}</span>
                <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
            </div>
        `;

        this.container.appendChild(notification);

        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.classList.remove('show');
                    setTimeout(() => {
                        if (notification.parentNode) {
                            notification.remove();
                        }
                    }, 150);
                }
            }, duration);
        }

        return notification;
    }

    getIcon(type) {
        const icons = {
            'success': 'fas fa-check-circle',
            'danger': 'fas fa-exclamation-triangle',
            'warning': 'fas fa-exclamation-circle',
            'info': 'fas fa-info-circle',
            'primary': 'fas fa-bell'
        };
        return icons[type] || icons['info'];
    }

    success(message, duration = 5000) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = 7000) {
        return this.show(message, 'danger', duration);
    }

    warning(message, duration = 6000) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration = 5000) {
        return this.show(message, 'info', duration);
    }
}

// Global notification instance
window.notify = new NotificationSystem();

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    .notification-popup {
        transform: translateX(0);
        transition: all 0.3s ease-out;
    }

    .notification-popup.fade:not(.show) {
        transform: translateX(100%);
    }
`;
document.head.appendChild(style);

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Convert flash messages to notifications
    const flashMessages = document.querySelectorAll('.alert:not(.notification-popup)');
    flashMessages.forEach(alert => {
        const message = alert.textContent.trim();
        const type = alert.className.includes('alert-danger') ? 'danger' :
                    alert.className.includes('alert-success') ? 'success' :
                    alert.className.includes('alert-warning') ? 'warning' : 'info';

        // Show as notification
        notify.show(message, type);

        // Hide original alert
        alert.style.display = 'none';
    });

    // Schedule item click handler
    document.addEventListener('click', function(e) {
        if (e.target.closest('.schedule-item')) {
            var scheduleItem = e.target.closest('.schedule-item');
            var scheduleId = scheduleItem.dataset.scheduleId;
            if (scheduleId) {
                showScheduleDetails(scheduleId);
            }
        }
    });

    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});

// Show schedule details in modal
function showScheduleDetails(scheduleId) {
    // This would typically fetch data via AJAX
    // For now, we'll show a placeholder modal
    var modal = new bootstrap.Modal(document.getElementById('scheduleModal'));
    modal.show();
}

// Attendance functions
function saveAttendance(scheduleId) {
    var form = document.getElementById('attendanceForm');
    var formData = new FormData(form);
    
    // Collect student attendance data
    var students = [];
    var studentRows = document.querySelectorAll('.student-row');
    
    studentRows.forEach(function(row) {
        var studentId = row.dataset.studentId;
        var statusSelect = row.querySelector('.attendance-status');
        var reasonInput = row.querySelector('.absence-reason');
        
        students.push({
            student_id: parseInt(studentId),
            status: statusSelect.value,
            reason: reasonInput ? reasonInput.value : ''
        });
    });
    
    var data = {
        schedule_id: parseInt(scheduleId),
        date: formData.get('date'),
        lesson_content: formData.get('lesson_content'),
        notes: formData.get('notes'),
        students: students
    };
    
    // Show loading spinner
    var submitBtn = document.getElementById('saveAttendanceBtn');
    var originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Đang lưu...';
    submitBtn.disabled = true;
    
    fetch('/teacher/save_attendance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', data.message);
        } else {
            showAlert('danger', data.message);
        }
    })
    .catch(error => {
        showAlert('danger', 'Có lỗi xảy ra khi lưu điểm danh');
        console.error('Error:', error);
    })
    .finally(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

// Show/hide absence reason input
function toggleAbsenceReason(selectElement) {
    var row = selectElement.closest('.student-row');
    var reasonInput = row.querySelector('.absence-reason');
    
    if (selectElement.value === 'absent_with_reason' || selectElement.value === 'absent_without_reason') {
        reasonInput.style.display = 'block';
        if (selectElement.value === 'absent_with_reason') {
            reasonInput.required = true;
        }
    } else {
        reasonInput.style.display = 'none';
        reasonInput.required = false;
        reasonInput.value = '';
    }
}

// Show alert message
function showAlert(type, message) {
    var alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'alertContainer';
        alertContainer.className = 'container mt-3';
        document.querySelector('main').prepend(alertContainer);
    }
    
    var alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        var bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}

// Confirm delete actions
function confirmDelete(message) {
    return confirm(message || 'Bạn có chắc chắn muốn xóa?');
}

// Format currency input
function formatCurrency(input) {
    var value = input.value.replace(/[^\d]/g, '');
    if (value) {
        input.value = parseInt(value).toLocaleString('vi-VN');
    }
}

// Search functionality
function searchTable(inputId, tableId) {
    var input = document.getElementById(inputId);
    var table = document.getElementById(tableId);
    var rows = table.getElementsByTagName('tr');
    
    input.addEventListener('keyup', function() {
        var filter = input.value.toLowerCase();
        
        for (var i = 1; i < rows.length; i++) {
            var row = rows[i];
            var cells = row.getElementsByTagName('td');
            var found = false;
            
            for (var j = 0; j < cells.length; j++) {
                if (cells[j].textContent.toLowerCase().indexOf(filter) > -1) {
                    found = true;
                    break;
                }
            }
            
            row.style.display = found ? '' : 'none';
        }
    });
}

// Export table to CSV
function exportTableToCSV(tableId, filename) {
    var table = document.getElementById(tableId);
    var csv = [];
    var rows = table.querySelectorAll('tr');
    
    for (var i = 0; i < rows.length; i++) {
        var row = [];
        var cols = rows[i].querySelectorAll('td, th');
        
        for (var j = 0; j < cols.length; j++) {
            row.push(cols[j].textContent.trim());
        }
        
        csv.push(row.join(','));
    }
    
    var csvContent = csv.join('\n');
    var blob = new Blob([csvContent], { type: 'text/csv' });
    var url = window.URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename || 'export.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}
