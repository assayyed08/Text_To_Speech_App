from django.contrib import admin
from .models import VisitorLog, UserDetail

@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ('date', 'visitor_count')  # Columns to display in the admin
    list_filter = ('date',)  # Filter by date
    search_fields = ('date',)  # Search bar for dates

@admin.register(UserDetail)
class UserDetailAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact_number', 'timestamp')  # Columns to display
    list_filter = ('timestamp',)  # Filter by timestamp
    search_fields = ('name', 'email', 'contact_number')  # Search bar

