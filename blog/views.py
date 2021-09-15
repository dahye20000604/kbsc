from django.shortcuts import render, redirect
from .models import Member, LithiumBattery
from django.contrib.auth.models import User
from django.contrib import auth

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
        try:
            user=User.objects.get(username=request.POST['id'])
            return render(request, 'signup.html', {'error':'User has already been taken'})
        except User.DoesNotExist:
            user=User.objects.create_user(
                request.POST['id'], password=request.POST['password'])
            Member.objects.create(user=user, nickname=request.POST['nickname'])
            auth.login(request, user)
            return redirect('/device', {"member":Member.objects.get(user=user), 'count':0})
    return render(request, 'signup.html')

def device_add(request):
    if request.method=='POST':
        user = request.user
        try:
            member=Member.objects.get(user=user)
            device=LithiumBattery.objects.get(member=member, name=request.POST['name'])
            return render(request, 'device_add.html', {{"name_error": "이미 존재하는 이름입니다."}})
        except LithiumBattery.DoesNotExist:
            device=LithiumBattery.create(
                member=member,
                name=request.POST['name'],
                category=request.POST['category'],
                battery_voltage=request.POST['battery_voltage'],
                battery_current=request.POST['nbattery_currentame'],
                battery_capacity=request.POST['battery_capacity'],
                rated_input_voltage=request.POST['rated_input_voltage'],
                rated_input_current=request.POST['rated_input_current'],
                charger_voltage=request.POST['charger_voltage'],
                charger_current=request.POST['charger_current'],
                purchase_period=request.POST['purchase_period'],
                status="None"
            )
            return redirect('/device', {"id":id})
    return render(request, 'device_add.html')

def device_start(request):
    user = request.user
    member=Member.objects.get(user=user)
    device=LithiumBattery.objects.get(member=member) #device가 하나라고 가정했을 때입니다. 수정 필요.
    if request.method == 'POST':
        device.start_battery = request.POST['start_battery']
        device.want_battery = request.POST['want_battery']
        predict_basis = device.loss * device.battery_capacity / device.charger_voltage / device.charger_current
        device.time_prediction = (float(device.want_battery) - float(device.start_battery)) / float(100.0) * float(predict_basis)
        device.save()
        return redirect('/device', {'device': device})
    return render(request, 'device_start.html', {'member':member, 'device' : device})

def device_stop(request):
    user = request.user
    member = Member.objects.get(user=user)
    device = LithiumBattery.objects.get(member=member) #device가 하나라고 가정했을 때입니다. 수정 필요.
    if request.method == 'POST':
        now_battery = request.POST['now_battery']
        real_chargingtime = request.POST['real_chargingtime']
        predict_basis = device.loss * device.battery_capacity / device.charger_voltage / device.charger_current
        device.time_prediction = (float(now_battery) - float(device.start_battery)) / float(100.0) * float(predict_basis)
        device.loss = float(device.loss) * float(real_chargingtime) / float(device.time_prediction)
        device.save()
        return redirect('/device', {'device' : device})
    return render(request, 'device_stop.html', {'member':member,'device':device})

def device(request):
    user=request.user
    member=Member.objects.get(user=user)
    try:
        device=LithiumBattery.objects.get(member=member)
        return render(request, 'device.html', {'member':member, 'device':device, 'count':len(device)})
    except:
        return render(request, 'device.html', {'member':member, 'count':0})