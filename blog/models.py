from django.db import models
from django.conf import settings
from pytz import timezone
from jsonfield import JSONField
from django.contrib.auth.models import User

class Member(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE,null=True)
    nickname = models.CharField(max_length = 5)
    def __str__(self):
        return self.nickname

class LithiumBattery(models.Model):
    member=models.ForeignKey(Member, on_delete=models.CASCADE)
    name=models.CharField(max_length=10)
    category=models.CharField(max_length=20, null = True)
    battery_voltage=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    battery_current=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    battery_capacity=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    rated_input_voltage=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    rated_input_current=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    charger_voltage=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    charger_current=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    purchase_period=models.DateField(editable=True, auto_now_add=True)

    charging_start_time=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20, null = True)

    loss=models.DecimalField(default=1.2, decimal_places=2, max_digits=20)
    min_voltage=models.DecimalField(default=3.7, decimal_places=2, max_digits=20)
    max_voltage=models.DecimalField(default=4.2, decimal_places=2, max_digits=20)

    start_battery = models.DecimalField(default = 30, decimal_places=3, max_digits=20)
    want_battery = models.DecimalField(default = 30, decimal_places=3, max_digits=20)
    time_prediction = models.DecimalField(default = 30, decimal_places=3, max_digits=20)

    @property
    def created_at_korean_time(self):
        korean_timezone=timezone(setting.TIME_ZONE)
        return self.created_at.astimezone(korean_timezone)

def prediction_chargingtime(LithiumBattery):
    predict_basis = LithiumBattery.loss * LithiumBattery.battery_capacity / charger_voltage / charger_current
    now_battery = int(input("현재 배터리의 양을 입력해주세요."))
    want_battery = int(input("몇 %까지 충전을 원하시나요?(80퍼 까지를 권장합니다.)"))
    return (want_battery - now_battery) / 100 * predict_basis

def update_loss(LithuimBattery):
    predict_basis = LithiumBattery.loss * LithiumBattery.battery_capacity / charger_voltage / charger_current
    now_battery = int(input("몇 %에서 충전을 시작하셨나요?"))
    want_battery = int(input("몇 %까지 충전을 하셨나요?"))
    real_chargingtime = int(input("충전 하는데 몇시간이 걸렸나요?"))
    time_prediction = (want_battery - now_battery) / 100 * predict_basis
    LithuimBattery.loss = LithiumBattery.loss * real_chargingtime / time_prediction