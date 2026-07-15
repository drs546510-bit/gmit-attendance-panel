from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, BRANCH_CHOICES, SEMESTER_CHOICES, Subject


class BootstrapFormMixin:
    """Adds Bootstrap 'form-control' / 'form-select' classes to every field
    automatically, so templates don't need to hand-style each widget."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css = 'form-select'
            elif isinstance(widget, forms.CheckboxInput):
                css = 'form-check-input'
            else:
                css = 'form-control'
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = (existing + ' ' + css).strip()


class TeacherSignupForm(BootstrapFormMixin, UserCreationForm):
    """Public signup form for teachers. The linked TeacherProfile is created
    with is_approved=False until an Admin approves it."""
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']


class StudentUserSignupForm(BootstrapFormMixin, UserCreationForm):
    """Signup for a student to get read-only login access, linked by USN."""
    usn = forms.CharField(max_length=20, required=True, label="Your USN")
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'usn', 'password1', 'password2']


class ExcelImportForm(BootstrapFormMixin, forms.Form):
    branch = forms.ChoiceField(choices=BRANCH_CHOICES)
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES)
    excel_file = forms.FileField(
        help_text="Excel file with columns: Sl.No, USN, Name (in that order). First row = header."
    )


class SubjectForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'branch', 'semester']


class TeacherAssignmentForm(BootstrapFormMixin, forms.Form):
    """Admin picks a Branch + Semester first, then a Subject that belongs
    to that exact branch+semester. The subject dropdown is filtered
    server-side based on whatever branch/semester was submitted (a plain
    page reload — no JS required, keeps things simple and reliable)."""
    branch = forms.ChoiceField(choices=BRANCH_CHOICES)
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES)
    subject = forms.ModelChoiceField(queryset=Subject.objects.none(), required=True)

    def __init__(self, *args, **kwargs):
        selected_branch = kwargs.pop('selected_branch', None)
        selected_semester = kwargs.pop('selected_semester', None)
        super().__init__(*args, **kwargs)
        if selected_branch and selected_semester:
            self.fields['subject'].queryset = Subject.objects.filter(
                branch=selected_branch, semester=selected_semester
            )
        else:
            self.fields['subject'].queryset = Subject.objects.all()
