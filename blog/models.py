from django.db import models
from django.conf import settings
from pytz import timezone
from jsonfield import JSONField
from django.contrib.auth.models import User

class Member(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE,null=True)
    nickname = models.CharField(max_length = 5)

class LithiumBattery(models.Model):
    member=models.ForeignKey(Member, on_delete=models.CASCADE)
    name=models.CharField(max_length=10)
    category=models.CharField(max_length=20)
    battery_voltage=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    battery_current=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    battery_capacity=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    rated_input_voltage=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    rated_input_current=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    charger_voltage=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    charger_current=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    purchase_period=models.DateField(editable=True, auto_now_add=True)

    charging_start_time=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20)

    loss=models.DecimalField(default=1.2, decimal_places=2, max_digits=20)
    min_voltage=models.DecimalField(default=3.7, decimal_places=2, max_digits=20)
    max_voltage=models.DecimalField(default=4.2, decimal_places=2, max_digits=20)

    @property
    def created_at_korean_time(self):
        korean_timezone=timezone(setting.TIME_ZONE)
        return self.created_at.astimezone(korean_timezone)

    def __str__(self):
        return 

