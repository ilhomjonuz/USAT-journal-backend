from django.core.mail import send_mail
from django.conf import settings
import threading


class EmailThread(threading.Thread):
    """
    Thread class for sending emails in the background
    """

    def __init__(self, subject, message, recipient_list, from_email=None):
        self.subject = subject
        self.message = message
        self.from_email = from_email or settings.DEFAULT_FROM_EMAIL
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            subject=self.subject,
            message=self.message,
            from_email=self.from_email,
            recipient_list=self.recipient_list,
            fail_silently=False,
        )


def send_email_async(subject, message, recipient_list, from_email=None):
    """
    Send email asynchronously using threading
    """
    EmailThread(subject, message, recipient_list, from_email).start()


def send_verification_email(email, verification_code):
    """
    Send verification code email asynchronously
    """
    subject = 'Email Verification Code'
    message = f'Your verification code is: {verification_code}'

    send_email_async(
        subject=subject,
        message=message,
        recipient_list=[email]
    )


def send_password_reset_email(email, verification_code):
    """
    Send password reset code email asynchronously
    """
    subject = 'Password Reset Code'
    message = f'Your password reset code is: {verification_code}'

    send_email_async(
        subject=subject,
        message=message,
        recipient_list=[email]
    )
