import threading
from django.core.mail import send_mail
from django.conf import settings


class EmailThread(threading.Thread):
    """
    Thread class for sending emails in the background
    """

    def __init__(self, subject, message, from_email, recipient_list, fail_silently=False):
        self.subject = subject
        self.message = message
        self.from_email = from_email
        self.recipient_list = recipient_list
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        """
        Run the thread to send email
        """
        send_mail(
            subject=self.subject,
            message=self.message,
            from_email=self.from_email,
            recipient_list=self.recipient_list,
            fail_silently=self.fail_silently
        )


def send_email_in_background(subject, message, recipient_list, fail_silently=False):
    """
    Send email in background thread

    Args:
        subject (str): Email subject
        message (str): Email message body
        recipient_list (list): List of recipient email addresses
        fail_silently (bool): Whether to suppress errors
    """
    from_email = settings.EMAIL_FROM
    EmailThread(subject, message, from_email, recipient_list, fail_silently).start()
