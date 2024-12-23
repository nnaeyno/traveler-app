from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from twilio.rest import Client

from user.models import Notification, User


@shared_task
def send_notification_email(
    place_creator_email, commenter_name, comment_text, place_name
):
    """
    Send an email notification to the creator of the place when someone comments on it.
    """
    subject = f"New comment on your place: {place_name}"
    message = f"""
    Hi,

    {commenter_name} commented on your place "{place_name}":

    "{comment_text}"

    Check it out on the platform!

    Regards,
    Your Platform Team
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [place_creator_email]

    # Send the email
    send_mail(subject, message, from_email, recipient_list)


@shared_task
def send_sms_notification(phone_number, message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message, from_=settings.TWILIO_PHONE_NUMBER, to=phone_number
    )


@shared_task(name="city.tasks.create_comment_notification")
def create_comment_notification(recipients, sender_id, place_name, comment_text):
    message = f"{sender_id} commented on your place '{place_name}': {comment_text}"
    recipients = User.objects.filter(id__in=recipients)
    sender = User.objects.get(id=sender_id)
    notifications = [
        Notification(recipient=recipient, sender=sender, message=message)
        for recipient in recipients
    ]

    Notification.objects.bulk_create(notifications)
