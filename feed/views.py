from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Profile, Idea
from .forms import IdeaForm, SignUpForm
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms


# Create your views here.

def home(request):
    if request.user.is_authenticated:
        form = IdeaForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                idea = form.save(commit=False)
                idea.user = request.user
                idea.save()
                messages.success(request, ('Your idea has been successfully submitted'))
                return redirect('home')
        ideas = Idea.objects.all().order_by('-created_at')
        return render(request, 'feed/home.html', {'ideas':ideas, 'form':form})
    else:
        ideas = Idea.objects.all().order_by('-created_at')
        return render(request, 'feed/home.html', {'ideas':ideas})


def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user) # query all users except self
        return render(request, 'feed/profile_list.html', {'profiles': profiles})
    else:
        messages.success(request, ('Login to view this page'))
        return redirect('home')
    

def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        ideas = Idea.objects.filter(user_id=pk).order_by('-created_at')
        # post form logic for follow/unfollow
        if request.method == 'POST':
            # get current user id
            current_user_profile = request.user.profile
            # get form data
            action = request.POST['follow']
            # decide to follow or unfollow
            if action == 'unfollow':
                current_user_profile.follows.remove(profile)
            elif action == 'follow':
                current_user_profile.follows.add(profile)
            # save profile
            current_user_profile.save()

        return render(request, 'feed/profile.html', {'profile': profile, 'ideas': ideas})
    else:
        messages.success(request, ('Login to view this page'))
        return redirect('home')
    

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username'] # refers to name= .... in template
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ('You have been logged in'))
            return redirect('home')
        else:
            messages.success(request, ('There was an error'))
            return redirect('login')
    else:
        return render(request, 'feed/login.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, ('You have been logged out'))
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # clean the form
            username = form.cleaned_data['username']
            # email = form.cleaned_data['email']
            # first_name = form.cleaned_data['first_name']
            # last_name = form.cleaned_data['last_name']
            password = form.cleaned_data['password1'] 
            # Log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ('You have successfully registered'))
            return redirect('home')
    return render(request, 'feed/register.html', {'form':form})


# class HomeView(ListView):
#     model = Post
#     template_name = 'feed/home.html'
#     ordering = ['-id'] # ideally by date, not in model yet


# class PostDetailView(DetailView):
#     model = Post
#     template_name = 'feed/post_detail.html'


# class AddPostView(CreateView):
#     model = Post
#     form_class = PostForm
#     template_name = 'feed/add_post.html'
#     # fields = ['title', 'body']
#     # fields = '__all__'


# class UpdatePostView(UpdateView):
#     model = Post
#     template_name = 'feed/update_post.html'
#     fields = ['title', 'title_tag', 'body']


# class DeletePostView(DeleteView):
#     model = Post
#     template_name = 'feed/delete_post.html'
#     success_url = reverse_lazy('home')