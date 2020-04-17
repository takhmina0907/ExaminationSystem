from django.core.mail import send_mail


def send_mail_wrapper(subject, message, receiver, html_message):

    send_mail(subject, message, None, [receiver], html_message=html_message)
