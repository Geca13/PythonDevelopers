from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm

def loginUser(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect("profiles")

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user:User.objects.get(username=username)
        except:
            messages.error(request, "username  does not exists")
        user = authenticate(request, username=username, password=password) 

        if user is not None:
            login(request, user)
            messages.success(request, "You logged in succesfully")

            return redirect('profiles')
        else:
            messages.error(request, "username or pass is incorrect")

    return render(request, 'users/login_register.html')

def logoutUser(request):
    logout(request)
    messages.success(request, "You logged out succesfully")
    return redirect('login') 


def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, "You Registered succesfully")

            login(request, user)
            return redirect('profiles')
        else:
             messages.success(request, "Something unexpected happened during registration , please try again ")   

    context = {'page':page, 'form':form}
    return render(request,'users/login_register.html', context)


def profiles(request):
    profiles = Profile.objects.all()
    context = {'profiles':profiles}
    return render(request, 'users/profiles.html', context)

def userProfile(request,pk):
    profile = Profile.objects.get(id=pk)
    topSkills = profile.skill_set.exclude(description__exact="")
    otherSkills = profile.skill_set.filter(description="")
    context = {'profile':profile, 'topSkills':topSkills, 'otherSkills': otherSkills}
    return render(request, 'users/user-profile.html', context)