from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


BRANCH_CHOICES = [
    ('EE', 'Electrical & Electronics Engineering'),
    ('CS', 'Computer Science & Engineering'),
    ('AI', 'Artificial Intelligence & Machine Learning'),
    ('EC', 'Electronics & Communication Engineering'),
    ('ME', 'Mechanical Engineering'),
    ('CE', 'Civil Engineering'),
    ('CSD', 'Computer Science & Design'),
]

SEMESTER_CHOICES = [(i, f"Semester {i}") for i in range(1, 9)]

ROLE_CHOICES = [
    ('ADMIN', 'Admin'),
    ('TEACHER', 'Teacher'),
    ('STUDENT', 'Student'),
]


class CustomUser(AbstractUser):
    """Extended user with a role. Django's is_staff/is_superuser still control
    access to the built-in /admin/ site; `role` drives our own dashboards."""
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class TeacherProfile(models.Model):
    """Every teacher account needs admin approval before they can mark attendance."""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    is_approved = models.BooleanField(default=False)
    requested_on = models.DateTimeField(auto_now_add=True)
    approved_on = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {'Approved' if self.is_approved else 'Pending'}"


class TeacherAssignment(models.Model):
    """Which branch + semester a teacher is allowed to mark attendance for.
    Assigned by the Admin only."""
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='assignments')
    branch = models.CharField(max_length=5, choices=BRANCH_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)

    class Meta:
        unique_together = ('teacher', 'branch', 'semester')

    def __str__(self):
        return f"{self.teacher.user.username} -> {self.branch} Sem {self.semester}"


class Student(models.Model):
    usn = models.CharField(max_length=20, unique=True, verbose_name="USN")
    name = models.CharField(max_length=150)
    branch = models.CharField(max_length=5, choices=BRANCH_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    user_account = models.OneToOneField(
        CustomUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='student_profile'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['usn']
        unique_together = ('usn', 'branch', 'semester')

    def __str__(self):
        return f"{self.usn} - {self.name}"


class Attendance(models.Model):
    STATUS_CHOICES = [('PRESENT', 'Present'), ('ABSENT', 'Absent')]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.usn} - {self.date} - {self.status}"
