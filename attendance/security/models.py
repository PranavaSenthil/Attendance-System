from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class UserType(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phoneno = models.CharField(max_length=10)
    gender = models.CharField(
        max_length=6,
        choices=[('MALE', 'MALE'),('FEMALE', 'FEMALE')]
    )
    is_admin = models.BooleanField(default=False)
    is_guard = models.BooleanField(default=False)

    def __str__(self):
        user_type = 'Admin' if self.is_admin else 'Guard' if self.is_guard else 'User'
        return f"{self.user.get_full_name() or self.user.username} - {user_type}"

class Attendance(models.Model):
    guard = models.ForeignKey(UserType, on_delete=models.CASCADE, limit_choices_to={'is_guard': True}, related_name='attendances')
    timestamp = models.DateTimeField(auto_now_add=True)
    day = models.CharField(max_length=10, editable=False)
    date = models.DateField(editable=False)
    time = models.TimeField(editable=False)
    selfie = models.ImageField(upload_to='selfies/')

    def save(self, *args, **kwargs):
        current_timestamp = datetime.now()
        self.day = current_timestamp.strftime('%A') 
        self.date = current_timestamp.date()          
        self.time = current_timestamp.time()          

        start_of_hour = current_timestamp.replace(minute=0, second=0, microsecond=0)
        end_of_hour = start_of_hour + timedelta(hours=1)

        if Attendance.objects.filter(
            guard=self.guard,
            timestamp__gte=start_of_hour,
            timestamp__lt=end_of_hour
        ).exists():
            raise ValueError("Selfie already uploaded for this hour.")

        super(Attendance, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.guard.user.get_full_name() or self.guard.user.username} - {self.timestamp}"

class Admin(models.Model):
    admin_type = models.OneToOneField(UserType, on_delete=models.CASCADE, limit_choices_to={'is_admin': True}, related_name='admin_profile')
    managed_guards = models.ManyToManyField(UserType, limit_choices_to={'is_guard': True}, related_name='managed_by_admins')

    def __str__(self):
        return self.admin_type.user.get_full_name() or self.admin_type.user.username
    
    def get_managed_guards(self):
        return self.managed_guards.all()
