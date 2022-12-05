from django.contrib.auth.models import User
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
import random
from django.core.mail import send_mail
from cryptography.fernet import Fernet 
from mechanize import Browser 
import favicon
from .models import Credentials

site = Browser()
site.set_handle_robots(False)

fernet = Fernet(settings.KEY)

def home(request):
    if request.method == "POST":
        if "signup-form" in request.POST:
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            password2 = request.POST.get("password2")
            # passwords dont match
            if password != password2:
                msg = "Passwords do not match. Please try again. !"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            # user already exists
            elif User.objects.filter(username=username).exists():
                msg = f"{username} already exists! !"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            # email already exists
            elif User.objects.filter(email=email).exists():
                msg = f"{email} already exists! !"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            else:
                User.objects.create_user(username, email, password)
                new_user = authenticate(request, username=username, password=password)
                if new_user is not None:
                    # 6 digit random verification code sent to email
                    verify = str(random.randint(100000, 999999))
                    global global_verify
                    global_verify = verify
                    subject="Rafikis Password Vault: Confirm Email"
                    body=f"Your 6-digit verfication code is  {verify}  . Please enter to finish subscribing and access your new vault."
                    sender=settings.EMAIL_HOST_USER
                    recipient= [new_user.email]
                    send_mail(subject, body, sender, recipient)
                    return render(request, "home.html", {
                        "verify":verify,
                        "user":new_user,
                    })
                    
        elif "logout" in request.POST:
            msg = f"{request.user}, You have successfully logged out."
            logout(request)
            messages.success(request, msg)
            return HttpResponseRedirect(request.path)
        
        elif 'login-form' in request.POST:
            username = request.POST.get("username")
            password = request.POST.get("password")
            new_login = authenticate(request, username=username, password=password)
            if new_login is None:
                msg = f"Login failed! Please check your username and/or password and try again. !"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            else:
                # 6 digit random verification code sent to email
                code = str(random.randint(100000, 999999))
                global global_code
                global_code = code
                subject="Rafikis Password Vault: Confirm Login"
                body=f"Your 6-digit confirmation code is  {code}  . Please enter to confirm email and login."
                sender=settings.EMAIL_HOST_USER
                recipient= [new_login.email]
                send_mail(subject, body, sender, recipient)
                return render(request, "home.html", {
                    "code":code,
                    "user":new_login,
                })

        elif "confirm" in request.POST:
            input_code = request.POST.get("code")
            user = request.POST.get("user")
            if input_code != global_code:
                msg =f"{input_code} entered: Code does not match confirmation code. Please try again."
                messages.error(request, msg)
                return HttpResponseRedirect("home.html")
            else:
                login(request, User.objects.get(username=user))
                msg = f"{request.user}, successfully logged in. Welcome back!"
                messages.success(request, msg)
                return HttpResponseRedirect(request.path)

        elif "subscribe" in request.POST:
            input_verify = request.POST.get("verify")
            user = request.POST.get("user")
            if input_verify != global_verify:
                msg =f"{input_verify} entered: Code does not match verification code. Please try again."
                messages.error(request, msg)
                return HttpResponseRedirect("home.html")
            else:
                login(request, User.objects.get(username=user))
                msg = f"{request.user}, Thank you for subscribing! You are now logged in."
                messages.success(request, msg)
                return HttpResponseRedirect(request.path)

        elif "add-credentials" in request.POST:
            url = request.POST.get("url")
            email = request.POST.get("email")
            password = request.POST.get("password")
            # encrypt data
            encrypted_email = fernet.encrypt(email.encode())
            encrypted_password = fernet.encrypt(password.encode())
            # checking if https:// added before url
            if "https://" not in url:
                try:
                    url = "https://" + url
                except:
                    url = request.POST.get("url")
            # get title of added website with Mechanize scraper Browser
            try:
                site.open(url)
                # clean title banner to just first word aka actual title
                title = site.title().split()[0]
                for char in "!-:":
                    title = title.replace(char, "")             
            except:
                title = url
            # get icon URL of added website w/ favicon
            try:
                icon = favicon.get(url)[0].url
            except:
                icon ="https://cdn-icons-png.flaticon.com/128/1006/1006771.png"
            # sava data in DB
            new_credentials = Credentials.objects.create(
                user=request.user,
                name=title,
                logo=icon,
                email=encrypted_email.decode(),
                password=encrypted_password.decode(),
            )
            msg = f"{title}  --  New site credentials succesfully added!"
            messages.success(request, msg)
            return HttpResponseRedirect(request.path)

        elif "generate" in request.POST:
            size_pass = request.POST.get("pass-length")
            size_pass = int(size_pass)
            if size_pass >= 8 and size_pass <= 24:
                allowed_chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^"
                new_pass = User.objects.make_random_password(length=size_pass, allowed_chars=allowed_chars)
                msg = f"Here is your new random password of length {size_pass}:    {new_pass}"
                messages.success(request, msg)
                return HttpResponseRedirect(request.path)
            else:
                msg = f"{size_pass} is an invalid input. Try again with a number between 8 and 24."
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)

        elif "delete" in request.POST:
            to_delete = request.POST.get("account-id")
            msg = f"{Credentials.objects.get(id=to_delete).name} successfully removed."
            Credentials.objects.get(id=to_delete).delete()
            messages.success(request, msg)
            return HttpResponseRedirect(request.path)

    context = {}
    if request.user.is_authenticated:     
        credentials = Credentials.objects.all().filter(user=request.user)
        for account in credentials:
            account.email = fernet.decrypt(account.email.encode()).decode()
            account.password = fernet.decrypt(account.password.encode()).decode()
        context = {
            "credentials":credentials,
        }


    return render(request, "home.html", context)
        