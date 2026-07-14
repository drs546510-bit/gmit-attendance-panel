from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, TeacherProfile, TeacherAssignment, Student, Attendance


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role', 'phone')}),
    )
    list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(TeacherProfile)
admin.site.register(TeacherAssignment)
admin.site.register(Student)
admin.site.register(Attendance)

admin.site.site_header = "GMIT Student Attendance Panel — Super Admin"
admin.site.site_title = "GMIT Attendance Admin"
admin.site.index_title = "Database Administration"
