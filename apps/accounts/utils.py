from django.core.mail import send_mail
from django.conf import settings
import threading
from django.utils.translation import gettext_lazy as _


class EmailThread(threading.Thread):
    """
    Thread class for sending emails in the background
    """

    def __init__(self, subject, message, html_message, recipient_list, from_email=None):
        self.subject = subject
        self.message = message
        self.html_message = html_message
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
            html_message=self.html_message,  # HTML formatda jo‘natish
        )


def send_email_async(subject, message, html_message, recipient_list, from_email=None):
    """
    Send email asynchronously using threading
    """
    EmailThread(subject, message, html_message, recipient_list, from_email).start()


def send_verification_email(email, verification_code):
    """
    Send verification code email asynchronously
    """
    subject = _('Email Verification Code')  # Tarjima ishlaydi

    message = _(
        "Your verification code is: {code}\n\n"
        "Do not share this code with anyone for security reasons."
    ).format(code=verification_code)

    html_message = f"""
        <p>{_('Your verification code is:')}</p>
        <h2 style="color: blue;">{verification_code}</h2>
        <p><strong>{_('Please do not share this code with anyone!')}</strong></p>
        <p>{_('If you did not request this, you can ignore this email.')}</p>
    """

    send_email_async(subject, message, html_message, [email])


def send_password_reset_email(email, verification_code):
    """
    Send password reset code email asynchronously
    """
    subject = _('Password Reset Code')

    message = _(
        "Your password reset code is: {code}\n\n"
        "Do not share this code with anyone for security reasons."
    ).format(code=verification_code)

    html_message = f"""
        <p>{_('Your password reset code is:')}</p>
        <h2 style="color: blue;">{verification_code}</h2>
        <p><strong>{_('Please do not share this code with anyone!')}</strong></p>
        <p>{_('If you did not request this, you can ignore this email.')}</p>
    """

    send_email_async(subject, message, html_message, [email])
