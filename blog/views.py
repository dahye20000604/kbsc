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
            return render(request, 'device.html', {"member":Member.objects.get(user=user)})
        else:
            return render(request, 'index.html', {'error': 'username or password is incorrect.'})
    else:
        return render(request, 'index.html')
    return render(request, 'index.html')

def signup(request):
    if request.method=='POST':
        try:
            user=User.objects.get(username=request.POST['id'])
            return render(request, 'index.html', {'error':'User has already been taken'})
        except User.DoesNotExist:
            user=User.objects.create_user(
                request.POST['id'], password=request.POST['password'])
            Member.objects.create(user=user, nickname=request.POST['nickname'])
            auth.login(request, user)
            return render('device.html', {"member":Member.objects.get(user=user)})
    return render(request, 'signup.html')

def device_add(request, id):
    if request.method=='POST':
        user = get_object_or_404(User, userid=id)
        try:
            member=Member.objects.get(user=user)
            device=LithiumBattery.objects.get(member=member)
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
            return render(request, 'device.html', {"id":id})
    return render(request, 'device_add.html')

def device(request, id):
    return render(request, 'device.html')