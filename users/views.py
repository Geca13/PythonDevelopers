from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm , ProfileForm, SkillForm
from django.db.models import Q
from .extractedMethods import searchProfiles, profilesPagination
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


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
            return redirect('edit-account')
        else:
             messages.success(request, "Something unexpected happened during registration , please try again ")   

    context = {'page':page, 'form':form}
    return render(request,'users/login_register.html', context)


def profiles(request):
    profiles, search_query = searchProfiles(request)
    custom_range, profiles = profilesPagination(request, profiles, 3) #the number is the number of results per page


    context = {'profiles':profiles, 'search-query':search_query,  'custom_range': custom_range}
    return render(request, 'users/profiles.html', context)

def userProfile(request,pk):
    profile = Profile.objects.get(id=pk)
    topSkills = profile.skill_set.exclude(description__exact="")
    otherSkills = profile.skill_set.filter(description="")
    context = {'profile':profile, 'topSkills':topSkills, 'otherSkills': otherSkills}
    return render(request, 'users/user-profile.html', context)

@login_required(login_url='login')
def userAccount(request):
    profile = request.user.profile
    skills = profile.skill_set.all()
    projects = profile.project_set.all();
    context = {'profile':profile, 'skills':skills, 'projects':projects}
    return render(request, 'users/account.html', context)    


@login_required(login_url='login')
def editAccount(request):  
    profile = request.user.profile
    form = ProfileForm(instance=profile)
    if request.method =='POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account')
    context ={'form':form}
    return render(request, 'users/profile_form.html', context) 


@login_required(login_url='login')
def createSkill(request):  
    profile = request.user.profile  
    form = SkillForm
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            form.save()
            messages.success(request, 'You added new skill , congratz')
            return redirect('account')
    context ={'form':form}
    return render(request, 'users/skill_form.html', context)  


@login_required(login_url='login')
def updateSkill(request, pk):  
    profile = request.user.profile 
    skill = profile.skill_set.get(id=pk) 
    form = SkillForm(instance=skill)
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'You updated a skill successfully')
            return redirect('account')
    context ={'form':form}
    return render(request, 'users/skill_form.html', context)


@login_required(login_url='login')
def deleteSkill(request, pk):  
    profile = request.user.profile 
    skill = profile.skill_set.get(id=pk)
    if request.method == 'POST':
       skill.delete(); 
       messages.success(request, 'You deleted a skill successfully') 
       return redirect('account')
    context ={'object':skill}
    return render(request, 'delete_object.html', context)             