from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('about/', views.about_page, name='about_page'),

    # Auth
    path('login/', views.GmitLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/teacher/', views.signup_teacher, name='signup_teacher'),
    path('signup/student/', views.signup_student, name='signup_student'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),

    # Admin panel
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/approve/<int:profile_id>/', views.approve_teacher, name='approve_teacher'),
    path('admin-panel/reject/<int:profile_id>/', views.reject_teacher, name='reject_teacher'),
    path('admin-panel/subjects/', views.manage_subjects, name='manage_subjects'),
    path('admin-panel/subjects/delete/<int:subject_id>/', views.delete_subject, name='delete_subject'),
    path('admin-panel/export/', views.export_reports, name='export_reports'),
    path('admin-panel/export/<int:subject_id>/', views.export_subject_attendance, name='export_subject_attendance'),
    path('admin-panel/assign/<int:profile_id>/', views.assign_teacher, name='assign_teacher'),
    path('admin-panel/assign/remove/<int:assignment_id>/', views.remove_assignment, name='remove_assignment'),
    path('admin-panel/import-students/', views.import_students, name='import_students'),
    path('admin-panel/branch/<str:branch>/', views.admin_branch_detail, name='admin_branch_detail'),
    path('admin-panel/chart-data/', views.admin_chart_data, name='admin_chart_data'),

    # Teacher panel — each subject (assignment) has its own attendance sheet
    path('teacher-panel/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher-panel/sheet/<int:assignment_id>/', views.teacher_attendance_sheet, name='teacher_attendance_sheet'),
    path('teacher-panel/mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('teacher-panel/chart-data/<int:assignment_id>/', views.teacher_chart_data, name='teacher_chart_data'),

    # Student panel
    path('student-panel/', views.student_dashboard, name='student_dashboard'),
]
