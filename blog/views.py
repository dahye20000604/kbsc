from django.shortcuts import render, redirect
from .models import Member
from django.contrib.auth.models import User
from django.contrib import auth

def index(request):
    if request.method=='POST':
        username=request.POST['id']
        password=request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return render(request, 'device.html', {"user":user, "username":username})
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
            return redirect('device')
    return render(request, 'signup.html')

def device_add(request):
    return render(request, 'device_add.html')

def device(request):
    return render(request, 'device.html')