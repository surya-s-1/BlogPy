from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *

# Create your views here.
@login_required(login_url='login')
def home(request):
    posts = Post.objects.all()
    return render(request, 'home.html', {'posts':posts})

@login_required(login_url='login')
def posts(request):
    if request.user.is_authenticated:
        return redirect('home')

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.filter(username=username)
        
        if user.exists():
            messages.info(request, 'Username already taken')
            return render(request, 'register.html', {
                'first_name':first_name,
                'last_name': last_name,
                'email': email,
                'password': password
            })
        
        user = User.objects.create_user(
            first_name = first_name,
            last_name = last_name,
            username = username,
            email = email
        )

        user.set_password(password)
        user.save()

        messages.info(request, 'User created successfully!')
        return redirect('login')
    
    return render(request, 'register.html')

def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Invalid username')
            return redirect('login')
        
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, 'Invalid password')
            return redirect('login')
        else:
            dj_login(request, user)
            return redirect('home')
    
    return render(request, 'login.html')

def logout(request):
    dj_logout(request)
    return redirect('login')

@login_required(login_url='login')
def userposts(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None

    if user is None:
        return redirect('home')
    
    posts = Post.objects.filter(user=user)
    
    return render(request, 'userposts.html', {'posts':posts, 'username': user.username})

@login_required(login_url='login')
def newpost(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        post = Post.objects.create(
            user=request.user,
            title=title,
            content=content
        )

        messages.info(request, 'Post created successfully!')

        post_id = post.id

        return redirect('postdetails', username=request.user.username, post_id=post_id)
    
    return render(request, 'newpost.html')

@login_required(login_url='login')
def postdetails(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        comment = request.POST.get('comment')
        
        user = request.user
        post = post

        comment = Comment.objects.create(
            post=post,
            user=user,
            comment=comment
        )

        messages.info(request, 'Commented successfully!')

        return redirect('postdetails', username=username, post_id=post_id)

    return render(request, 'postdetails.html', {'post':post})