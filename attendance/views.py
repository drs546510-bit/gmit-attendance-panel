import json
from datetime import date

import openpyxl
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import TeacherSignupForm, StudentUserSignupForm, ExcelImportForm, TeacherAssignmentForm
from .models import (
    CustomUser, TeacherProfile, TeacherAssignment, Student, Attendance,
    BRANCH_CHOICES, SEMESTER_CHOICES,
)

BRANCH_DICT = dict(BRANCH_CHOICES)


def is_admin(user):
    # Superusers (created via `createsuperuser`) are always treated as Admins,
    # even before anyone manually sets role='ADMIN' on them.
    return user.is_authenticated and (user.role == 'ADMIN' or user.is_superuser)


class GmitLoginView(LoginView):
    template_name = 'attendance/login.html'


@login_required
def dashboard_redirect(request):
    user = request.user
    if user.role == 'ADMIN' or user.is_superuser:
        return redirect('admin_dashboard')
    if user.role == 'TEACHER':
        return redirect('teacher_dashboard')
    return redirect('student_dashboard')


def signup_teacher(request):
    if request.method == 'POST':
        form = TeacherSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'TEACHER'
            user.email = form.cleaned_data['email']
            user.phone = form.cleaned_data.get('phone', '')
            user.save()
            TeacherProfile.objects.create(user=user, is_approved=False)
            messages.success(
                request,
                "Account created! Your teacher account needs Admin approval "
                "before you can mark attendance."
            )
            return redirect('login')
    else:
        form = TeacherSignupForm()
    return render(request, 'attendance/signup_teacher.html', {'form': form})


def signup_student(request):
    if request.method == 'POST':
        form = StudentUserSignupForm(request.POST)
        if form.is_valid():
            usn = form.cleaned_data['usn'].strip().upper()
            try:
                student = Student.objects.get(usn=usn)
            except Student.DoesNotExist:
                form.add_error('usn', 'No student record found with this USN. Ask your teacher/admin to add you first.')
            else:
                if student.user_account_id:
                    form.add_error('usn', 'This USN is already linked to another login account.')
                else:
                    user = form.save(commit=False)
                    user.role = 'STUDENT'
                    user.email = form.cleaned_data['email']
                    user.save()
                    student.user_account = user
                    student.save()
                    messages.success(request, "Account created! You can now log in to view your attendance.")
                    return redirect('login')
    else:
        form = StudentUserSignupForm()
    return render(request, 'attendance/signup_student.html', {'form': form})


# ---------------- ADMIN ----------------

@login_required
def admin_dashboard(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Admins only.")

    pending_teachers = TeacherProfile.objects.filter(is_approved=False).select_related('user')
    approved_teachers = TeacherProfile.objects.filter(is_approved=True).select_related('user')

    branch_stats = []
    for code, label in BRANCH_CHOICES:
        total_students = Student.objects.filter(branch=code).count()
        branch_stats.append({'code': code, 'label': label, 'total_students': total_students})

    context = {
        'pending_teachers': pending_teachers,
        'approved_teachers': approved_teachers,
        'branch_stats': branch_stats,
        'total_students': Student.objects.count(),
        'total_teachers': approved_teachers.count(),
        'today_marked': Attendance.objects.filter(date=timezone.localdate()).count(),
        'branch_choices': BRANCH_CHOICES,
        'semester_choices': SEMESTER_CHOICES,
    }
    return render(request, 'attendance/admin_dashboard.html', context)


@login_required
def approve_teacher(request, profile_id):
    if not is_admin(request.user):
        return HttpResponseForbidden("Admins only.")
    profile = get_object_or_404(TeacherProfile, id=profile_id)
    profile.is_approved = True
    profile.approved_on = timezone.now()
    profile.save()
    messages.success(request, f"{profile.user.username} has been approved as a teacher.")
    return redirect('admin_dashboard')


@login_required
def reject_teacher(request, profile_id):
    if not is_admin(request.user):
        return HttpResponseForbidden("Admins only.")
    profile = get_object_or_404(TeacherProfile, id=profile_id)
    username = profile.user.username
    profile.user.delete()
    messages.warning(request, f"Teacher request for {username} was rejected and removed.")
    return redirect('admin_dashboard')


@login_required
def assign_teacher(request, profile_id):
    if not is_admin(request.user):
        return HttpResponseForbidden("Admins only.")
    profile = get_object_or_404(TeacherProfile, id=profile_id, is_approved=True)
    if request.method == 'POST':
        form = TeacherAssignmentForm(request.POST)
        if form.is_valid():
            TeacherAssignment.objects.get_or_create(
                teacher=profile,
                branch=form.cleaned_data['branch'],
                semester=form.cleaned_data['semester'],
            )
            messages.success(request, "Assignment added.")
            return redirect('assign_teacher', profile_id=profile.id)
    else:
        form = TeacherAssignmentForm()
    assignments = profile.assignments.all()
    return render(request, 'attendance/assign_teacher.html', {
        'profile': profile, 'form': form, 'assignments': assignments,
    })


@login_required
def remove_assignment(request, assignment_id):
    if not is_admin(request.user):
        return HttpResponseForbidden("Admins only.")
    assignment = get_object_or_404(TeacherAssignment, id=assignment_id)
    profile_id = assignment.teacher_id
    assignment.delete()
    return redirect('assign_teacher', profile_id=profile_id)


@login_required
def import_students(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Admins only.")
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            branch = form.cleaned_data['branch']
            semester = int(form.cleaned_data['semester'])
            excel_file = request.FILES['excel_file']
            try:
                wb = openpyxl.load_workbook(excel_file, data_only=True)
                sheet = wb.active
                created, skipped = 0, 0
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    if not row or len(row) < 3:
                        continue
                    _, usn, name = row[0], row[1], row[2]
                    if not usn or not name:
                        continue
                    usn = str(usn).strip().upper()
                    name = str(name).strip()
                    obj, was_created = Student.objects.get_or_create(
                        usn=usn, branch=branch, semester=semester,
                        defaults={'name': name},
                    )
                    if was_created:
                        created += 1
                    else:
                        skipped += 1
                messages.success(
                    request,
                    f"Import complete for {BRANCH_DICT[branch]} - Semester {semester}: "
                    f"{created} new students added, {skipped} already existed."
                )
                return redirect('admin_dashboard')
            except Exception as exc:
                messages.error(request, f"Could not read the Excel file: {exc}")
    else:
        form = ExcelImportForm()
    return render(request, 'attendance/import_students.html', {'form': form})


@login_required
def admin_branch_detail(request, branch):
    if not is_admin(request.user):
        return HttpResponseForbidden("Admins only.")
    if branch not in BRANCH_DICT:
        return HttpResponseForbidden("Unknown branch.")

    sem_data = []
    for sem, _ in SEMESTER_CHOICES:
        students = Student.objects.filter(branch=branch, semester=sem)
        count = students.count()
        today_present = Attendance.objects.filter(
            student__branch=branch, student__semester=sem,
            date=timezone.localdate(), status='PRESENT'
        ).count()
        sem_data.append({'semester': sem, 'total': count, 'present_today': today_present})

    return render(request, 'attendance/admin_branch_detail.html', {
        'branch': branch, 'branch_label': BRANCH_DICT[branch], 'sem_data': sem_data,
    })


@login_required
def admin_chart_data(request):
    if not is_admin(request.user):
        return JsonResponse({'error': 'forbidden'}, status=403)

    labels, percentages = [], []
    for code, label in BRANCH_CHOICES:
        total = Attendance.objects.filter(student__branch=code).count()
        present = Attendance.objects.filter(student__branch=code, status='PRESENT').count()
        pct = round((present / total) * 100, 1) if total else 0
        labels.append(code)
        percentages.append(pct)
    return JsonResponse({'labels': labels, 'data': percentages})


# ---------------- TEACHER ----------------

@login_required
def teacher_dashboard(request):
    if request.user.role != 'TEACHER':
        return HttpResponseForbidden("Teachers only.")
    profile = get_object_or_404(TeacherProfile, user=request.user)
    if not profile.is_approved:
        return render(request, 'attendance/teacher_pending.html')

    assignments = profile.assignments.all()
    return render(request, 'attendance/teacher_dashboard.html', {
        'assignments': assignments, 'branch_dict': BRANCH_DICT,
    })


@login_required
def teacher_attendance_sheet(request, branch, semester):
    if request.user.role != 'TEACHER':
        return HttpResponseForbidden("Teachers only.")
    profile = get_object_or_404(TeacherProfile, user=request.user)
    if not profile.is_approved:
        return HttpResponseForbidden("Your account is awaiting admin approval.")
    if not profile.assignments.filter(branch=branch, semester=semester).exists():
        return HttpResponseForbidden("You are not assigned to this branch/semester.")

    semester = int(semester)
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        selected_date = date.fromisoformat(selected_date_str)
    else:
        selected_date = timezone.localdate()

    students = Student.objects.filter(branch=branch, semester=semester).order_by('usn')
    today_records = {
        a.student_id: a.status
        for a in Attendance.objects.filter(student__in=students, date=selected_date)
    }

    rows = []
    for i, student in enumerate(students, start=1):
        total_days = student.attendance_records.count()
        present_days = student.attendance_records.filter(status='PRESENT').count()
        absent_days = total_days - present_days
        rows.append({
            'sl_no': i,
            'student': student,
            'status_today': today_records.get(student.id),
            'present_days': present_days,
            'absent_days': absent_days,
            'total_days': total_days,
        })

    context = {
        'branch': branch,
        'branch_label': BRANCH_DICT[branch],
        'semester': semester,
        'rows': rows,
        'selected_date': selected_date,
        'now': timezone.localtime(),
    }
    return render(request, 'attendance/attendance_sheet.html', context)


@login_required
@require_POST
def mark_attendance(request):
    if request.user.role != 'TEACHER':
        return JsonResponse({'error': 'forbidden'}, status=403)
    profile = get_object_or_404(TeacherProfile, user=request.user)
    if not profile.is_approved:
        return JsonResponse({'error': 'not approved'}, status=403)

    try:
        payload = json.loads(request.body)
        student_id = payload['student_id']
        status = payload['status']
        date_str = payload.get('date')
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({'error': 'bad request'}, status=400)

    if status not in ('PRESENT', 'ABSENT'):
        return JsonResponse({'error': 'invalid status'}, status=400)

    student = get_object_or_404(Student, id=student_id)
    if not profile.assignments.filter(branch=student.branch, semester=student.semester).exists():
        return JsonResponse({'error': 'not assigned to this class'}, status=403)

    record_date = date.fromisoformat(date_str) if date_str else timezone.localdate()

    attendance, _ = Attendance.objects.update_or_create(
        student=student, date=record_date,
        defaults={'status': status, 'marked_by': request.user},
    )

    total_days = student.attendance_records.count()
    present_days = student.attendance_records.filter(status='PRESENT').count()
    absent_days = total_days - present_days

    return JsonResponse({
        'ok': True,
        'status': attendance.status,
        'present_days': present_days,
        'absent_days': absent_days,
        'total_days': total_days,
        'marked_at': timezone.localtime(attendance.marked_at).strftime('%d-%b-%Y %I:%M %p'),
    })


@login_required
def teacher_chart_data(request, branch, semester):
    if request.user.role != 'TEACHER':
        return JsonResponse({'error': 'forbidden'}, status=403)
    semester = int(semester)
    students = Student.objects.filter(branch=branch, semester=semester)
    labels, present_counts, absent_counts = [], [], []
    for s in students:
        total = s.attendance_records.count()
        present = s.attendance_records.filter(status='PRESENT').count()
        labels.append(s.usn)
        present_counts.append(present)
        absent_counts.append(total - present)
    return JsonResponse({'labels': labels, 'present': present_counts, 'absent': absent_counts})


# ---------------- STUDENT (read-only) ----------------

@login_required
def student_dashboard(request):
    if request.user.role != 'STUDENT':
        return HttpResponseForbidden("Students only.")
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return render(request, 'attendance/student_no_record.html')

    records = student.attendance_records.all().order_by('-date')
    total_days = records.count()
    present_days = records.filter(status='PRESENT').count()
    absent_days = total_days - present_days
    percentage = round((present_days / total_days) * 100, 1) if total_days else 0

    return render(request, 'attendance/student_dashboard.html', {
        'student': student,
        'records': records[:60],
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'percentage': percentage,
        'branch_label': BRANCH_DICT[student.branch],
    })


# ---------------- ABOUT PAGE ----------------

def about_page(request):
    """Public 'About this app' page — no login required, so it also works
    as a nice landing/credits page."""
    return render(request, 'attendance/about.html')
