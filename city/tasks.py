from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from user.models import Notification
from twilio.rest import Client


@shared_task
def send_notification_email(place_creator_email, commenter_name, comment_text, place_name):
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
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number
    )


@shared_task(name='city.tasks.create_comment_notification')
def create_comment_notification(recipient_id, sender_id, place_name, comment_text):
    message = f"{sender_id} commented on your place '{place_name}': {comment_text}"
    Notification.objects.create(
        recipient_id=recipient_id,
        sender_id=sender_id,
        message=message
    )
