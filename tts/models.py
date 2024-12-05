from django.db import models
from django.utils.timezone import now

class UserDetail(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=15)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.name} - {self.email}"

class VisitorLog(models.Model):
    date = models.DateField(unique=True)
    visitor_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.date} - {self.visitor_count} visitors"
