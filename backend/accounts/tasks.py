from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from django.core.mail import send_mail
from .models import Event


@shared_task
def send_event_reminders():
    # Replace with the number of days before the event to send the reminder
    days_before_event = 1

    # Get all events happening in the next `days_before_event` days
    upcoming_events = Event.objects.filter(date__lte=timezone.now() + timedelta(days=days_before_event))

    for event in upcoming_events:
        # Get all users who have saved this event
        users = event.users_saved.all()

        for user in users:
            # Send a reminder email to each user
            subject = f'Reminder: {event.title} is happening soon!'
            message = f'Don\'t forget, {event.title} is happening on {event.date}.'
            from_email = 'CRISTOCENTRIC <luca.stancu@gmail.com>'
            recipient_list = [user.email]
            send_mail(subject, message, from_email, recipient_list)