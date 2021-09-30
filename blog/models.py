from django.db import models
from django.conf import settings
from jsonfield import JSONField
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np

class Member(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE,null=True)
    nickname = models.CharField(max_length = 10)
    def __str__(self):
        return self.nickname

class LithiumBattery(models.Model):
    member=models.ForeignKey(Member, on_delete=models.CASCADE)
    name=models.CharField(max_length=20)
    category=models.CharField(max_length=20, null = True)
    battery_voltage=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    battery_current=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    battery_capacity=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    rated_input_current=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    charger_voltage=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    charger_current=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    charger_watt=models.DecimalField(default=0, decimal_places=2, max_digits = 20)
    purchase_period=models.DateField(editable=True, auto_now_add=False)

    status=models.CharField(max_length=20, null = True)

    loss=models.DecimalField(default=1.2, decimal_places=10, max_digits=20)
    loss_record = []
    manual_prediction = models.DecimalField(default = 0, decimal_places=10, max_digits=20)
    min_voltage=models.DecimalField(default=3.7, decimal_places=2, max_digits=20)
    max_voltage=models.DecimalField(default=4.2, decimal_places=2, max_digits=20)

    start_battery = models.IntegerField(default = 0)
    want_battery = models.IntegerField(default = 0)

    time_prediction_entire = models.DecimalField(default = 30, decimal_places=3, max_digits=20)
    time_prediction_day = models.IntegerField(default = 0)
    time_prediction_hour = models.IntegerField(default = 0)
    time_prediction_min = models.IntegerField(default = 0)
    time_prediction_sec = models.IntegerField(default = 0)
    
    now_time = models.DateTimeField(auto_now_add = True)
    charging_start_time = models.DateTimeField(auto_now_add=True)
    charging_finish_time = models.DateTimeField(auto_now_add=True)
    @property
    def created_at_korean_time(self):
        korean_timezone=timezone(setting.TIME_ZONE)
        return self.created_at.astimezone(korean_timezone)

device_list = LithiumBattery.objects.all

def initial_loss(device_list, now_device):
    battery_capacity = np.array([])
    charger_voltage = np.array([])
    charger_current = np.array([])
    purchase_period = np.array([])
    loss = np.array([])
    for device in device_list:
        battery_capacity = np.append(battery_capacity, device.battery_capacity)
        charger_voltage = np.append(charger_voltage, device.charger_voltage)
        charger_current = np.append(charger_current, device.charger_current)
        purchase_period = np.append(purchase_period, (device.purchase_period- timezone.now().date()).days)
        loss = np.append(loss, device.loss)
    if(np.std(battery_capacity) == 0 or np.std(charger_voltage) == 0 or np.std(charger_current) == 0 or np.std(purchase_period) == 0):
        return [1.2]
    battery_capacity_scaled = (battery_capacity - np.mean(battery_capacity)) / np.std(battery_capacity) 
    charger_voltage_scaled = (charger_voltage - np.mean(charger_voltage)) / np.std(charger_voltage)
    charger_current_scaled = (charger_current - np.mean(charger_current)) / np.std(charger_current)
    purchase_period_scaled = (purchase_period - np.mean(purchase_period)) / np.std(purchase_period)
    X = np.array([battery_capacity_scaled, charger_voltage_scaled, charger_current_scaled, purchase_period_scaled])
    X = X.reshape(-1,4)
    model = LinearRegression()
    model.fit(X,loss)
    data = np.array([])
    data = np.append(data, (now_device.battery_capacity - np.mean(battery_capacity)) / np.std(battery_capacity))
    data = np.append(data, (now_device.charger_voltage - np.mean(charger_voltage)) / np.std(charger_voltage))
    data = np.append(data, (now_device.charger_current - np.mean(charger_current)) / np.std(charger_current))
    data = np.append(data, ((now_device.purchase_period -timezone.now().date()).days - np.mean(purchase_period)) / np.std(purchase_period))
    return model.predict(data.reshape(1,4))

def Predict_Basis(device):
    battery_Wh = 0
    charger_W = 0
    if device.battery_capacity != 0:
        battery_Wh = device.battery_capacity
    elif (device.battery_current != 0) & (device.battery_voltage != 0):
        battery_Wh = device.battery_current * device.battery_voltage
    if (device.charger_voltage != 0) & (device.charger_current != 0):
        charger_W = device.charger_voltage * device.charger_current
    elif device.charger_watt != 0:
        charger_W = device.charger_watt
    return device.loss * battery_Wh / charger_W
