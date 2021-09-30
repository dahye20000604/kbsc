from django.shortcuts import render, redirect
from .models import Member, LithiumBattery, Predict_Basis, initial_loss
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
            return render(request, 'index.html', {'error': '아이디 또는 비밀번호가 잘못 입력 되었습니다.'})
    return render(request, 'index.html')

def signup(request):
    if request.method=='POST':
        if 'signup' in request.POST:
            try:
                user=User.objects.get(username=request.POST['id'])
                return render(request, 'signup.html', {'error':'이미 사용중인 아이디 입니다.'})
            except User.DoesNotExist:
                if request.POST['password']!=request.POST['passwordcheck']:
                    return render(request ,'signup.html', {'error': '비밀번호가 일치하지 않습니다.'})
                user=User.objects.create_user(request.POST['id'], password=request.POST['password'])
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
            dic={
                "member":member,
                "name":request.POST['name'],
                "category":request.POST['category'],
                "battery_voltage":request.POST['battery_voltage'],
                "battery_current":request.POST['battery_current'],
                "battery_capacity":request.POST['battery_capacity'],
                "manual_prediction":request.POST['manual_prediction'],
                "rated_input_current":request.POST['rated_input_current'],
                "charger_voltage":request.POST['charger_voltage'],
                "charger_current":request.POST['charger_current'],
                "charger_watt":request.POST['charger_watt'],
                "purchase_period":request.POST['purchase_period']
            }
            try:
                device=LithiumBattery.objects.get(member=member, name=request.POST['name'])
                dic.update({"error":"이미 존재하는 이름입니다."})
                return render(request, 'device_add.html', dic)
            except LithiumBattery.DoesNotExist:
                if dic["category"]=="":
                    dic.update({"error":"종류를 선택해주세요"})
                    return render(request, 'device_add.html', dic)
                elif (dic["battery_voltage"]=="" or dic["battery_current"]=="") and dic["battery_capacity"]=="":
                    dic.update({"error":"배터리 정보를 더 입력해주세요"})
                    return render(request, 'device_add.html', dic)
                elif (dic["charger_voltage"]=="" or dic["charger_current"]==""):
                    dic.update({"error":"충전기 정보를 더 입력해주세요"})
                    return render(request, 'device_add.html', dic)
                elif (dic["purchase_period"]==""):
                    dic.update({"error":"구매 시기를 대략적으로 입력해주세요"})
                    return render(request, 'device_add.html', dic)
                else:
                    print(dic["purchase_period"])
                    LithiumBattery.objects.create(
                    member=member,
                    name=dic["name"],
                    category=dic["category"],
                    battery_voltage=dic["battery_voltage"] if dic["battery_voltage"] else 0,
                    battery_current=dic["battery_current"] if dic["battery_current"] else 0,
                    battery_capacity=dic["battery_capacity"] if dic["battery_capacity"] else float(dic["battery_voltage"]) * float(dic["battery_current"]),
                    manual_prediction=dic["manual_prediction"] if dic["manual_prediction"] else 0,
                    rated_input_current=dic["rated_input_current"] if dic["rated_input_current"] else 0,
                    charger_voltage=dic["charger_voltage"] if dic["charger_voltage"] else 0,
                    charger_current=dic["charger_current"] if dic["charger_current"] else 0,
                    charger_watt=dic["charger_watt"] if dic["charger_watt"] else 0,
                    purchase_period=dic["purchase_period"],
                    status="None"
                    )
                    device = LithiumBattery.objects.get(member=member, name = dic['name'])
                    if(device.manual_prediction == 0):
                        category = ['phone', 'kickboard', 'tablet', 'laptop', 'earphone']
                        for i in category:
                            if (device.category == i):
                                device.loss = initial_loss(LithiumBattery.objects.filter(category = i), device)[0]
                                device.save()
                    else:
                        device.loss = device.charger_voltage * device.charger_current * device.manual_prediction / device.battery_capacity
                        device.save()
                    device.loss_record.append(device.loss)
                    device.save()
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
        predict_basis = Predict_Basis(device)
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
    if (request.method == 'POST') and ("update" in request.POST):
        now_battery = request.POST['now_battery']
        
        device.now_time = timezone.now()
        difference = device.now_time - device.charging_start_time

        real_chargingtime = difference.seconds / 3600  #시간 단위
        predict_basis = Predict_Basis(device)
        device.time_prediction_entire = (float(now_battery) - float(device.start_battery)) / float(100.0) * float(predict_basis)

        loss = float(device.loss) * float(real_chargingtime) / float(device.time_prediction_entire)
        device.loss = (loss*4 + float(device.loss)*1) / 5
        device.loss_record.append(device.loss)
        device.status="None"
        device.save()
        return redirect('/device',{'member':member,'device':LithiumBattery.objects.filter(member=member)})
    elif (request.method == 'POST') and ("not_update" in request.POST):
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
    if (request.method == 'POST') and ("Charging Finish with update" in request.POST):
        now_battery = request.POST['now_battery']
        
        device.now_time = timezone.now()
        difference = device.now_time - device.charging_start_time

        real_chargingtime = difference.seconds / 3600  #시간 단위
        predict_basis = Predict_Basis(device)
        device.time_prediction_entire = (float(now_battery) - float(device.start_battery)) / float(100.0) * float(predict_basis)

        if (float(now_battery)<=80):
            loss = float(device.loss) * float(real_chargingtime) / float(device.time_prediction_entire)
            device.loss = (loss*4 + float(device.loss)*1) / 5
            device.loss_record.append(device.loss)
            device.status="None"
            device.save()
        device.status="None"
        device.save()
        return redirect('/device',{'member':member,'device':LithiumBattery.objects.filter(member=member)})
    elif (request.method == 'POST') and ("Charging Finish without update" in request.POST):
        device.status = "None"
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
    user = request.user
    member = Member.objects.get(user=user)
    device = LithiumBattery.objects.get(member=member, name=device_name)
    if request.method=='POST':
        if 'done' in request.POST:
            device.name=device.name if request.POST['name']=="" else request.POST['name'] 
            device.battery_voltage=device.battery_voltage if request.POST['battery_voltage']=="" else request.POST['battery_voltage'] 
            device.battery_current=device.battery_current if request.POST['battery_current']=="" else request.POST['battery_current']
            device.battery_capacity=device.battery_capacity if request.POST['battery_capacity']=="" else request.POST['battery_capacity']
            device.rated_input_voltage=device.rated_input_voltage if request.POST['rated_input_voltage']=="" else request.POST['rated_input_voltage']
            device.rated_input_current=device.rated_input_current if request.POST['rated_input_current']=="" else request.POST['rated_input_current']
            device.charger_voltage=device.charger_voltage if request.POST['charger_voltage']=="" else request.POST['charger_voltage']
            device.charger_current=device.charger_current if request.POST['charger_current']=="" else request.POST['charger_current']
            device.charger_watt=device.charger_watt if request.POST['charger_watt']=="" else request.POST['charger_watt']
            device.purchase_period=device.purchase_period if request.POST['purchase_period']=="" else request.POST['purchase_period']
            device.status="None"     
            device.save()           
            return redirect('/device', {"member":member})
        elif 'back' in request.POST:
            return redirect('/device')
    return render(request, 'device_edit.html', {'device':device})

def device_delete(request, device_name):
    user = request.user
    member = Member.objects.get(user=user)
    device = LithiumBattery.objects.get(member=member, name=device_name)
    device.delete()
    return redirect('/device', {"member":member})