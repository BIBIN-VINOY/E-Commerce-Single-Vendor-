from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_save
from .models import User
from django.db.models.signals import post_save



@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        print("Welcome email signal fired")

        send_mail(
            subject="Welcome to E-Commerce",
            message=f"""
Hello {instance.username},

Welcome to our E-Commerce website!

Your account has been created successfully.

Happy Shopping!

Regards,
E-Commerce Team
BIBIN
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=False,
        )

        
@receiver(user_logged_in)
def send_login_email(sender, request, user, **kwargs):
    send_mail(
        subject="Login Successful",
        message=f"""
Hello {user.username},

Your account has been logged in successfully.

If this wasn't you, please change your password immediately.

Thank you,
E-COMMERCE TEAM
BIBIN
""",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

