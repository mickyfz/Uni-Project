from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'university_id', 'department', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'department')
    fieldsets = UserAdmin.fieldsets + (
        ('University Role Info', {'fields': ('role', 'university_id', 'department', 'phone', 'profile_pic')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('University Role Info', {'fields': ('role', 'university_id', 'department', 'phone', 'profile_pic')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
