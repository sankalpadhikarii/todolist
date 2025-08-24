from django.db import models
from django.conf import settings
from django.utils import timezone
from twilio.rest import Client

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    is_finished = models.BooleanField(default=False)
    is_notified = models.BooleanField(default=False)
    is_assigned = models.BooleanField(default=False)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='item_assigned')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='item_created')

    class Meta:
        ordering = ('due_date',)

    def __str__(self):
        return self.title

    def has_alarm(self):
        return self.due_date is not None

    def has_expired(self):
        if self.has_alarm():
            return timezone.now() > self.due_date
        else:
            return False

    def status(self):
        if self.is_finished:
            return 'Finished'
        elif self.has_expired():
            return 'Expired'
        else:
            return 'In progress'

    def save(self, *args, **kwargs):
        if self.is_assigned:
            # Use placeholders instead of real keys and numbers
            account_sid = 'YOUR_TWILIO_ACCOUNT_SID_HERE'
            auth_token = 'YOUR_TWILIO_AUTH_TOKEN_HERE'
            client = Client(account_sid, auth_token)

            message = client.messages.create(
                body=f"{self.title} has been assigned by {self.assigned_by} due {self.due_date}",
                from_='+YOUR_TWILIO_PHONE_NUMBER',
                to='+RECIPIENT_PHONE_NUMBER'
            )

            print(message.sid)
        return super().save(*args, **kwargs)
