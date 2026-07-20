from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import Conversation, Message


# =========================
# ADMIN PANEL CUSTOMIZATION
# =========================

admin.site.site_header = "AI Chat Administration"
admin.site.site_title = "AI Chat Admin"
admin.site.index_title = "Administration Dashboard"


# =========================
# USER ADMIN
# =========================

admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "id",
        "username",
        "email",
        "is_active",
        "is_staff",
        "date_joined",
        "last_login",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    search_fields = (
        "username",
        "email",
    )

    ordering = (
        "-date_joined",
    )


# =========================
# CONVERSATION ADMIN
# =========================

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "title",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__username",
        "title",
    )

    ordering = (
        "-updated_at",
    )


# =========================
# MESSAGE ADMIN
# =========================

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "conversation",
        "role",
        "created_at",
    )

    list_filter = (
        "role",
        "created_at",
    )

    search_fields = (
        "content",
        "conversation__title",
        "conversation__user__username",
    )

    ordering = (
        "-created_at",
    )