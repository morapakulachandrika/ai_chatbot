import re

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
import json
from django.http import JsonResponse
from .models import Conversation, Message
from django.http import JsonResponse
from .models import Conversation, Message
# =========================
# REGISTER
# =========================

def register_view(request):

    if request.user.is_authenticated:
        return redirect("chat_dashboard")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Passwords must match
        if password != confirm_password:
            messages.error(
                request,
                "Passwords do not match."
            )
            return redirect("register")


        # Minimum 6 characters
        if len(password) < 6:
            messages.error(
                request,
                "Password must be at least 6 characters."
            )
            return redirect("register")


        # At least one uppercase letter
        if not re.search(r"[A-Z]", password):
            messages.error(
                request,
                "Password must contain at least one uppercase letter."
            )
            return redirect("register")


        # At least one lowercase letter
        if not re.search(r"[a-z]", password):
            messages.error(
                request,
                "Password must contain at least one lowercase letter."
            )
            return redirect("register")


        # At least one number
        if not re.search(r"[0-9]", password):
            messages.error(
                request,
                "Password must contain at least one number."
            )
            return redirect("register")


        # At least one special character
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            messages.error(
                request,
                "Password must contain at least one special character."
            )
            return redirect("register")


        # Username validation
        if User.objects.filter(username=username).exists():
            messages.error(
                request,
                "Username already exists."
            )
            return redirect("register")
        # Username validation
        if User.objects.filter(username=username).exists():
            messages.error(
                request,
                "Username already exists."
            )
            return redirect("register")

        # Email validation
        if User.objects.filter(email=email).exists():
            messages.error(
                request,
                "Email already exists."
            )
            return redirect("register")

        # =========================
        # CREATE USER
        # =========================

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )


        # =========================
        # WELCOME EMAIL TO USER
        # =========================

        user_html_content = render_to_string(
            "chat/emails/welcome_email.html",
            {
                "username": user.username,
            }
        )

        welcome_email = EmailMultiAlternatives(
            subject="Welcome to AI Chat",
            body=f"""
        Hello {user.username},

        Your AI Chat account has been created successfully.

        Username: {user.username}

        You can now login and start using AI Chat.

        Thank you,
        AI Chat Team
        """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )

        welcome_email.attach_alternative(
            user_html_content,
            "text/html"
        )

        welcome_email.send(
            fail_silently=True
        )


        # =========================
        # ADMIN REGISTRATION EMAIL
        # =========================

        admin_html_content = render_to_string(
            "chat/emails/admin_registration_email.html",
            {
                "username": user.username,
                "email": user.email,
            }
        )

        admin_email = EmailMultiAlternatives(
            subject="New User Registration - AI Chat",
            body=f"""
        A new user has registered on AI Chat.

        Username: {user.username}
        Email: {user.email}

        You can manage this user from the AI Chat Admin Panel.

        AI Chat System
        """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.EMAIL_HOST_USER],
        )

        admin_email.attach_alternative(
            admin_html_content,
            "text/html"
        )

        admin_email.send(
            fail_silently=True
        )


        # =========================
        # SUCCESS
        # =========================

        messages.success(
            request,
            "Account created successfully. Please login."
        )

        return redirect("login")

    return render(
        request,
        "chat/register.html"
    )


# =========================
# LOGIN
# =========================

def login_view(request):

    if request.user.is_authenticated:
        return redirect("chat_dashboard")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("chat_dashboard")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "chat/login.html"
    )


# =========================
# CHAT DASHBOARD
# =========================

@login_required(login_url="login")
def chat_dashboard(request):

    conversations = Conversation.objects.filter(
        user=request.user
    ).order_by(
        "-is_pinned",
        "-updated_at"
    )

    return render(
        request,
        "chat/chat_dashboard.html",
        {
            "conversations": conversations
        }
    )


# =========================
# PROFILE
# =========================

@login_required(login_url="login")
def profile_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        # Check duplicate email
        if User.objects.exclude(
            id=request.user.id
        ).filter(
            email=email
        ).exists():

            messages.error(
                request,
                "Email already exists."
            )

            return redirect("profile")

        # Update user
        request.user.username = username
        request.user.email = email

        request.user.save()

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect("profile")

    return render(
        request,
        "chat/profile.html"
    )


# =========================
# LOGOUT
# =========================

def logout_view(request):

    logout(request)

    return redirect("login")

@login_required(login_url="login")
def send_message(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required."},
            status=405
        )

    try:
        data = json.loads(request.body)

        user_message = data.get(
            "message",
            ""
        ).strip()

        conversation_id = data.get(
            "conversation_id"
        )

        if not user_message:
            return JsonResponse(
                {"error": "Message cannot be empty."},
                status=400
            )

        # Get existing conversation
        if conversation_id:

            try:
                conversation = Conversation.objects.get(
                    id=conversation_id,
                    user=request.user
                )

            except Conversation.DoesNotExist:

                return JsonResponse(
                    {"error": "Conversation not found."},
                    status=404
                )

        else:

            # Create a new conversation
            conversation = Conversation.objects.create(
                user=request.user,
                title=user_message[:50]
            )

        # Save user's message
        Message.objects.create(
            conversation=conversation,
            role="user",
            content=user_message
        )

        # Temporary response
        # We will connect the real AI model next.
        ai_response = (
            f"You said: {user_message}"
        )

        # Save assistant response
        Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=ai_response
        )

        return JsonResponse({
            "success": True,
            "conversation_id": conversation.id,
            "conversation_title": conversation.title,
            "user_message": user_message,
            "ai_response": ai_response,
        })

    except json.JSONDecodeError:

        return JsonResponse(
            {"error": "Invalid JSON request."},
            status=400
        )

    except Exception as error:

        print("Send message error:", error)

        return JsonResponse(
            {"error": "Something went wrong."},
            status=500
        )
# =========================
# LOAD CONVERSATION
# =========================

@login_required(login_url="login")
def load_conversation(request, conversation_id):

    try:
        conversation = Conversation.objects.get(
            id=conversation_id,
            user=request.user
        )

        conversation_messages = conversation.messages.order_by(
            "created_at"
        )

        messages_data = [
            {
                "role": message.role,
                "content": message.content
            }
            for message in conversation_messages
        ]

        return JsonResponse({
            "success": True,
            "conversation_id": conversation.id,
            "title": conversation.title,
            "messages": messages_data,
        })

    except Conversation.DoesNotExist:

        return JsonResponse(
            {
                "error": "Conversation not found."
            },
            status=404
        )
@login_required(login_url="login")
def pin_conversation(request, conversation_id):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required."},
            status=405
        )

    try:
        conversation = Conversation.objects.get(
            id=conversation_id,
            user=request.user
        )

        # Toggle pin status
        conversation.is_pinned = not conversation.is_pinned
        conversation.save()

        return JsonResponse({
            "success": True,
            "is_pinned": conversation.is_pinned
        })

    except Conversation.DoesNotExist:
        return JsonResponse(
            {"error": "Conversation not found."},
            status=404
        )
# =========================
# RENAME CONVERSATION
# =========================

@login_required(login_url="login")
def rename_conversation(request, conversation_id):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required."},
            status=405
        )

    try:
        data = json.loads(request.body)

        new_title = data.get(
            "title",
            ""
        ).strip()

        if not new_title:
            return JsonResponse(
                {"error": "Title cannot be empty."},
                status=400
            )

        conversation = Conversation.objects.get(
            id=conversation_id,
            user=request.user
        )

        conversation.title = new_title[:200]
        conversation.save()

        return JsonResponse({
            "success": True,
            "title": conversation.title
        })

    except Conversation.DoesNotExist:
        return JsonResponse(
            {"error": "Conversation not found."},
            status=404
        )


# =========================
# DELETE CONVERSATION
# =========================

@login_required(login_url="login")
def delete_conversation(request, conversation_id):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required."},
            status=405
        )

    try:
        conversation = Conversation.objects.get(
            id=conversation_id,
            user=request.user
        )

        conversation.delete()

        return JsonResponse({
            "success": True
        })

    except Conversation.DoesNotExist:
        return JsonResponse(
            {"error": "Conversation not found."},
            status=404
        )