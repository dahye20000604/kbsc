from django.shortcuts import render, redirect
from .models import Member, LithiumBattery
from django.contrib.auth.models import User
from django.contrib import auth
from django.conf import settings
#from pytz import timezone
from django.utils import timezone
from datetime import datetime, timedelta

def index(request):
    if request.method=='POST':
        username=request.POST['id']
        password=request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            member=Member.objects.get(user=user)
            try:
                device=LithiumBattery.objects.get(member=member)
                return redirect('/device',{'member':member, 'device':device})
            except:
                return redirect('/device',{'member':member, 'count':0})
        else:
            return render(request, 'index.html', {'error': 'username or password is incorrect.'})
    return render(request, 'index.html')

def signup(request):
    if request.method=='POST':
        if 'signup' in request.POST:
            try:
                user=User.objects.get(username=request.POST['id'])
                return render(request, 'signup.html', {'error':'User has already been taken'})
            except User.DoesNotExist:
                if request.POST['password']!=request.POST['passwordcheck']:
                    return render(request, '')
                user=User.objects.create_user(
                    request.POST['id'], password=request.POST['password'])
                Member.objects.create(user=user, nickname=request.POST['nickname'])
                auth.login(request, user)
                return redirect('/device', {"member":Member.objects.get(user=user), 'count':0})
        elif 'back' in request.POST:
            return redirect('/')
    
    return render(request, 'signup.html')

def device_add(request):
    if request.method=='POST':
        if 'done' in request.POST:
            user = request.user
            member=Member.objects.get(user=user)
            try:
                device=LithiumBattery.objects.get(member=member, name=request.POST['name'])
                return render(request, 'device_add.html', {{"name_error": "이미 존재하는 이름입니다."}})
            except LithiumBattery.DoesNotExist:
                LithiumBattery.objects.create(
                    member=member,
                    name=request.POST['name'],
                    category=request.POST['category'],
                    battery_voltage=request.POST['battery_voltage'],
                    battery_current=request.POST['battery_current'],
                    battery_capacity=request.POST['battery_capacity'],
                    rated_input_voltage=request.POST['rated_input_voltage'],
                    rated_input_current=request.POST['rated_input_current'],
                    charger_voltage=request.POST['charger_voltage'],
                    charger_current=request.POST['charger_current'],
                    purchase_period=request.POST['purchase_period'],
                    status="None"
                )
                return redirect('/device', {"member":member})
        elif 'back' in request.POST:
            return redirect('/device')
    return render(request, 'device_add.html')

def device_start(request, device_name):
    user = request.user
    member=Member.objects.get(user=user)
    device=LithiumBattery.objects.get(member=member, name=device_name)
    if (request.method == 'POST') and ("Charging Start" in request.POST):
        device.start_battery = request.POST['start_battery']
        device.want_battery = request.POST['want_battery']
        predict_basis = device.loss * device.battery_capacity / device.charger_voltage / device.charger_current
        device.time_prediction_entire = (float(device.want_battery) - float(device.start_battery)) / float(100.0) * float(predict_basis)
        sec = int(device.time_prediction_entire * 3600)

        device.time_prediction_day = sec // 86400
        device.time_prediction_hour = sec // 3600
        device.time_prediction_min = (sec // 60) % 60
        device.time_prediction_sec = sec % 60

        device.charging_start_time = timezone.now()
        charging_time = timedelta(days = device.time_prediction_day, hours = device.time_prediction_hour, minutes = device.time_prediction_min, seconds = device.time_prediction_sec) #days 추가
        device.charging_finish_time = device.charging_start_time + charging_time
        device.now_time = timezone.now()

        device.status="Charging"
        device.save()
        return redirect('/device', {'memeber' : member, 'device' : LithiumBattery.objects.filter(member=member)})
    elif  (request.method == 'POST') and ("back" in request.POST):
        return redirect('/device')
    return render(request, 'device_start.html', {'member':member, 'device' : device})

def device_stop(request, device_name):
    user = request.user
    member = Member.objects.get(user=user)
    device = LithiumBattery.objects.get(member=member, name=device_name)
    if (request.method == 'POST') and ("Charging Stop" in request.POST):
        now_battery = request.POST['now_battery']
        
        device.now_time = timezone.now()
        difference = device.now_time - device.charging_start_time

        real_chargingtime = difference.seconds / 3600  #시간 단위
        predict_basis = device.loss * device.battery_capacity / device.charger_voltage / device.charger_current
        device.time_prediction_entire = (float(now_battery) - float(device.start_battery)) / float(100.0) * float(predict_basis)

        device.loss = float(device.loss) * float(real_chargingtime) / float(device.time_prediction_entire)
        device.status="None"
        device.save()
        return redirect('/device',{'member':member,'device':LithiumBattery.objects.filter(member=member)})
    elif  (request.method == 'POST') and ("back" in request.POST):
        return redirect('/device')
    return render(request, 'device_stop.html', {'member':member,'device':device})

def device_complete(request, device_name):
    user = request.user
    member = Member.objects.get(user=user)
    device = LithiumBattery.objects.get(member=member, name=device_name)
    if (request.method == 'POST') and ("Charging Finish" in request.POST):
        now_battery = request.POST['now_battery']
        
        device.now_time = timezone.now()
        difference = device.now_time - device.charging_start_time

        real_chargingtime = difference.seconds / 3600  #시간 단위
        predict_basis = device.loss * device.battery_capacity / device.charger_voltage / device.charger_current
        device.time_prediction_entire = (float(now_battery) - float(device.start_battery)) / float(100.0) * float(predict_basis)

        if (float(now_battery)<=80):
            device.loss = float(device.loss) * float(real_chargingtime) / float(device.time_prediction_entire)
        device.status="None"
        device.save()
        return redirect('/device',{'member':member,'device':LithiumBattery.objects.filter(member=member)})
    elif  (request.method == 'POST') and ("back" in request.POST):
        return redirect('/device')
    return render(request, 'device_complete.html', {'member':member,'device':device})

def device(request):
    user=request.user
    member=Member.objects.get(user=user)
    device=LithiumBattery.objects.filter(member=member)
    if device:
        for i in device:
            if i.status=="Charging":
                i.now_time = timezone.now()
                difference = i.charging_finish_time - i.now_time
                i.time_prediction_day = difference.days
                i.time_prediction_hour = difference.seconds // 3600
                i.time_prediction_min = (difference.seconds % 3600) // 60
                i.time_prediction_sec = difference.seconds % 60
                if i.time_prediction_day == -1:
                    i.status = "Complete"
            i.save()
    return render(request, 'device.html', {'member':member, 'device':device, 'count':len(device)})

def device_edit(request, device_name):
    user=request.user
    member=Member.objects.get(user=user)
    device=LithiumBattery.objects.get(member=member, name=device_name)
    if device.status=="None":
        return render(request, 'device_start.html', {'member':member, 'device':device})
    elif device.status=="Charging":
        return render(request, 'device_stop.html', {'member':member, 'device':device})
    elif device.status == "Complete":
        return render(request, 'device_complete.html', {'member':member, 'device':device})
