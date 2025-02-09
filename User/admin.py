from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

# class UserAdmin(BaseUserAdmin):
#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         ('Personal Info', {'fields': ('first_name', 'last_name', 'photo', 'bio')}),
#         ('Roles and Permissions', {'fields': ('role', 'year', 'status', 'is_active', 'is_staff', 'is_superuser')}),
#         ('Important Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'year'),
#         }),
#     )
#     list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
#     search_fields = ('email', 'first_name', 'last_name')
#     ordering = ('email',)

admin.site.register(User)
