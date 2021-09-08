from django.shortcuts import render

def index(request):
    #로그인

    #회원가입 버튼 클릭시 signup.html로 연결되게 구현
    return render(request, 'index.html')

def signin(request):
    return render(request, 'signup.html')
def signup(request):
    #회원가입
    return render(request, 'signup.html')