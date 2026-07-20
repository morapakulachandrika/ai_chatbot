from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [

    # Authentication
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # Chat Dashboard
    path(
        "chat/",
        views.chat_dashboard,
        name="chat_dashboard"
    ),

    # Profile
    path(
        "profile/",
        views.profile_view,
        name="profile"
    ),

    path(
    "forgot-password/",
    auth_views.PasswordResetView.as_view(
        template_name="chat/forgot_password.html",

        # Plain-text fallback email
        email_template_name="chat/password_reset_email.txt",

        # Professional HTML email
        html_email_template_name="chat/emails/password_reset_email.html",

        subject_template_name="chat/password_reset_subject.txt",

        success_url=reverse_lazy("password_reset_done"),
    ),
    name="password_reset",
    ),

    # Password Reset Email Sent
    path(
        "forgot-password/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="chat/password_reset_done.html"
        ),
        name="password_reset_done",
    ),

    # Set New Password
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="chat/password_reset_confirm.html",
            success_url=reverse_lazy(
                "password_reset_complete"
            ),
        ),
        name="password_reset_confirm",
    ),

    # Password Reset Complete
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="chat/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]