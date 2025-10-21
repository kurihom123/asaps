from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model

from ..models.organization_model import Association, Position

# Create your models here.

User = get_user_model()


class Level(models.Model):
    name = models.CharField(max_length=35)
    abbr = models.CharField(max_length=10)

    class Meta:
        db_table = 'level'

    def __str__(self):
        return f'{self.abbr}'


class UserProfile(models.Model):
    SEX = (
        ('male', 'Male'),
        ('female', 'Female')
    )
    sex = models.CharField(max_length=8, choices=SEX)
    phone = models.CharField(max_length=10, unique=True)
    postal_address = models.CharField(max_length=45)
    photo = models.ImageField(upload_to='img', unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_profile')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='user_level', null=True)
    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='user_profile_association')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='user_profile_position', default='leader')

    class Meta:
        db_table = 'user_profile'

    def __str__(self):
        return f'{self.user}'


class UserLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_log')
    activity = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_logs'

    def __str__(self):
        return self.activity



class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_reports')
    report_about = models.CharField(max_length=150)
    report_file = models.FileField(upload_to='reports/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'report'

    def __str__(self):
        return self.report_about


class ReportView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'report_views'
        unique_together = ('user', 'report')

    def __str__(self):
        return f'{self.user} viewed {self.report}'
