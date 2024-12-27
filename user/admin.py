from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import User, Notification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'status', 'display_photo', 'created_at',
                    'is_active', 'is_staff')
    list_filter = ('status', 'is_active', 'is_staff', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    filter_horizontal = ('cities', 'groups', 'user_permissions')
    readonly_fields = ('created_at', 'display_photo_large')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': ('username', 'first_name', 'last_name', 'profile_photo',
                       'display_photo_large')
        }),
        (_('Locations'), {
            'fields': ('cities',)
        }),
        (_('Status'), {
            'fields': ('status',)
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups',
                       'user_permissions'),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'created_at', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

    def display_photo(self, obj):
        if obj.profile_photo:
            return format_html('<img src="{}" height="50"/>', obj.profile_photo.url)
        return "No photo"

    display_photo.short_description = 'Profile Photo'

    def display_photo_large(self, obj):
        if obj.profile_photo:
            return format_html('<img src="{}" height="200"/>', obj.profile_photo.url)
        return "No photo"

    display_photo_large.short_description = 'Profile Photo Preview'


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'message_preview', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__username', 'recipient__email',
                     'sender__username', 'sender__email', 'message')
    raw_id_fields = ('recipient', 'sender')
    readonly_fields = ('created_at',)
    actions = ['mark_as_read', 'mark_as_unread']

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message

    message_preview.short_description = 'Message Preview'

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    mark_as_read.short_description = "Mark selected notifications as read"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)

    mark_as_unread.short_description = "Mark selected notifications as unread"

    fieldsets = (
        ('Notification Details', {
            'fields': ('recipient', 'sender', 'message', 'is_read')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


admin.site.register(Notification, NotificationAdmin)