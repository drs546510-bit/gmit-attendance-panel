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


class Subject(models.Model):
    """A subject taught within a specific branch + semester, e.g.
    'Physics' for EE Sem 1. Created by the Admin. Each subject gets its
    own independent attendance sheet, even for the same branch+semester."""
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, blank=True)
    branch = models.CharField(max_length=5, choices=BRANCH_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)

    class Meta:
        unique_together = ('name', 'branch', 'semester')
        ordering = ['branch', 'semester', 'name']

    def __str__(self):
        return f"{self.name} ({self.branch} Sem {self.semester})"


class TeacherAssignment(models.Model):
    """Which subject (within a branch + semester) a teacher is allowed to
    mark attendance for. Assigned by the Admin only. A teacher can hold
    multiple assignments across different subjects/branches/semesters."""
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name='assignments',
        null=True, blank=True,  # null only for old pre-subject rows created before this update
    )

    # Kept for convenience/backward compatibility with existing code and
    # data (they always match subject.branch / subject.semester).
    branch = models.CharField(max_length=5, choices=BRANCH_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)

    class Meta:
        unique_together = ('teacher', 'subject')

    def save(self, *args, **kwargs):
        # Keep branch/semester in sync with the chosen subject automatically.
        if self.subject_id:
            self.branch = self.subject.branch
            self.semester = self.subject.semester
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.teacher.user.username} -> {self.subject}"


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
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name='attendance_records',
        null=True, blank=True,  # null only for old pre-subject rows; new rows always set this
    )
    date = models.DateField(default=timezone.localdate)
    session_number = models.PositiveSmallIntegerField(
        default=1,
        help_text="Lets the same subject be marked more than once on the same day "
                   "(e.g. two periods of Physics). Session 1, Session 2, etc."
    )
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        # A student can now have one attendance row PER SUBJECT, PER DAY,
        # PER SESSION — instead of only one row per subject per day. This
        # lets a teacher mark two separate periods of the same subject on
        # the same day without one overwriting the other.
        unique_together = ('student', 'subject', 'date', 'session_number')
        ordering = ['-date', 'session_number']

    def __str__(self):
        subject_label = self.subject.name if self.subject else "General"
        return f"{self.student.usn} - {subject_label} - {self.date} (Session {self.session_number}) - {self.status}"
