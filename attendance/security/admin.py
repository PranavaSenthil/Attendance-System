from django.contrib import admin
from .models import *
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('user', 'phoneno', 'gender', 'is_admin', 'is_guard')
    search_fields = ('user__username', 'phoneno')
    list_filter = ('is_admin', 'is_guard')

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('guard', 'timestamp', 'day', 'date', 'time')
    search_fields = ('guard__user__username', 'guard__user__first_name', 'guard__user__last_name')
    list_filter = ('guard', 'day', 'date')
    ordering = ('-timestamp',)


class AdminAdmin(admin.ModelAdmin):
    list_display = ('admin_type',)
    filter_horizontal = ('managed_guards',)

admin.site.register(UserType, UserTypeAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Admin, AdminAdmin)