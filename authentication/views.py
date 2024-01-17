from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from .tokens import generate_token
from django.core.mail import EmailMessage,send_mail
from GFG import settings

# Create your views here.
def home(request):
    return render(request,"home.html")

def signup(request):
    if request.method =="POST":
        username=request.POST["username"]
        first_name=request.POST["firstname"]
        last_name=request.POST["lastname"]
        email=request.POST["email"]
        password=request.POST["password1"]
        confirm_password=request.POST["password2"]
        if User.objects.filter(username=username):
            messages.error(request,"Username already exists")
            return redirect("home")
        if User.objects.filter(email=email):
            messages.error(request,"Email Already Exists")
            return redirect("home")
        if password!=confirm_password:
            messages.error(request,"Password Didn't match")
            return redirect("home")
        myuser=User.objects.create_user(username,email,password)
        myuser.first_name=first_name
        myuser.last_name=last_name
        myuser.is_active=False
        myuser.save()
        messages.success(request,"Your account has been created Successfully. We have sent you an confirmation email.\n Please confirm you email in order to activate your account")

        #welcome email
        subject = "Welcome to Library-Login"
        message="Hello"+myuser.first_name+"!! \n"+"Welcom to Swamivivekanand Library \n Thankyou \n We have also sent you a confirmation email, Please confirm you email address in order to activate your account \n Thankyou, \n Prajesh Waghela"
        from_email=settings.EMAIl_HOST_USER
        to_list=[myuser.email]
        send_mail(subject,message,from_email,to_list,fail_silently=True)

        #Email address Confirmation email
        current_site=get_current_site(request)
        email_subject="Confirm your email @ Swamivivekanad Library"
        message2=render_to_string("email_confirmation.html",{"name":myuser.first_name,"domain":current_site,"uid":urlsafe_base64_encode(force_bytes(myuser.pk)),
        "token":generate_token.make_token(myuser)})
        email=EmailMessage(
            email_subject,
            message2,
            settings.EMAIl_HOST_USER,
            [myuser.email],
            
        )
        email.fail_silently=True
        email.send()
        return redirect('signin')
    return render(request,"signup.html")

def signin(request):
    if request.method =="POST":
        username=request.POST["username"]
        password=request.POST["password1"]
        user=authenticate(username=username,password=password)
        if user:
            login(request,user)
            fname=user.first_name
            return render(request,"index.html",{"fname":fname})
        else:
            messages.error(request,"Invalid Credentials")
            return redirect('home')
    return render(request,"signin.html")

def signout(request):
    logout(request)
    messages.success(request,"Successfully Logged Out")
    return redirect('home')

def activate(request,uidb64,token):
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        myuser=User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser=None 

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active=True
        myuser.save()
        login(request,myuser)
        return redirect("home")
    else:
        return render(request,"activation_Failed.html")