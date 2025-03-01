from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from .models import Profile,Post,Comment,like,Story
from django.contrib.auth.decorators import login_required
from .forms import postform,postedit,storyform
from django.urls import reverse
import datetime



def Registration(req):
    if req.method=='POST':
        first_name=req.POST.get('first_name')
        last_name=req.POST.get('last_name')
        username=req.POST.get('username')
        email=req.POST.get('email')
        password=req.POST.get('password')

        User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password
        )
        return redirect('Login')
    else:
        return render(req,'Registeration.html')

def Login(req):
    if req.method=='POST':
        username=req.POST.get('username')
        password=req.POST.get('password')

        user=auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(req,user)
            return redirect('home')
        else:
            messages.error(req,'Invalid Credential')
            return redirect('Login')
    else:
        return render(req,'Login.html')
    
def logout(req):
    auth.logout(req)
    return redirect('/')

def profile(req):
    user=req.user
    try:
        profile=Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)
    posts=Post.objects.filter(user__username=user.username)
    postcount=posts.count()
    following=profile.following.count()
    follower=profile.follower.count()
    return render(req,'Profile.html',{'profile':profile,'posts':posts,'postcount':postcount,'following':following,'follower':follower})

@login_required
def Editprofile(req):
    user=req.user
    try:
       profile=Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile(user=user)

    if req.method == 'POST':
        profile.bio = req.POST.get('bio')
        profile.profile_picture = req.FILES.get('profile_picture')
        profile.save()
        return redirect('profile')
    return render(req, 'Editprofile.html',{'profile': profile})

def home(req):
    user=req.user
    posts=Post.objects.all()
    time = datetime.datetime.now() - datetime.timedelta(hours=24)
    stories=Story.objects.filter(created_at__gte=time)
    try:
        profile=Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile=Profile.objects.create(user=user)
    allprofile=Profile.objects.exclude(user=user)
    return render(req,'home.html',{'posts':posts,'profile':profile,'stories':stories,'allprofile':allprofile})

def createpost(req):
    if req.method=='POST':
        form=postform(req.POST,req.FILES)
        if form.is_valid():
            Post=form.save(commit=False)
            Post.user=req.user
            Post.save()
            messages.success(req,'Post Created Successfully')
            return redirect('home')
        else:
            messages.error(req,'Invalid form data')
            return render(req,'postform.html',{'form':form})
    else:
        form=postform()
        return render(req,'postform.html',{'form':form})

def deletepost(req,post_id):
    post=Post.objects.get(id=post_id)
    post.delete()
    messages.success(req,'Deleted Successfully')
    return redirect('home')

def editpost(req,post_id):
    post=Post.objects.get(id=post_id)
    if req.method=='POST':
       form=postedit(req.POST,req.FILES,instance=post)
       if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form=postedit(instance=post)

    return render(req,'editpost.html',{'form':form ,'post':post})

@login_required
def addcomment(req, post_id):
    if req.method == 'POST':
        post = Post.objects.get(id=post_id)
        text = req.POST.get('text')
        if text:
            comment = Comment.objects.create(
                post=post,
                user=req.user,
                text=text
            )
            comment.save()
            return redirect('home')
    return render(req, 'home.html', {'post_id': post_id})
    
def addstory(req):
    user = req.user
    profile = Profile.objects.get(user=user)  
    if req.method == 'POST':
        form = storyform(req.POST, req.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.user = user
            story.profile = profile
            story.save()
            messages.success(req, 'Story added successfully')
            return redirect('home')
        else:
            messages.error(req, 'Something went wrong')
            return render(req, 'Story.html', {'form': form})
    else:
        form = storyform()
        return render(req, 'Story.html', {'form': form})

def viewstory(req,str_id):
    stories=Story.objects.get(id=str_id)
    return render(req,'viewstory.html',{'stories':stories})

def likeview(req,post_id):
    user=req.user
    post=Post.objects.get(id=post_id)
    current_likes=post.likes
    liked=like.objects.filter(user=user,post=post).count()
    if not liked:
        liked=like.objects.create(user=user,post=post)
        current_likes=current_likes+1
    else:
        liked=like.objects.filter(user=user,post=post).delete()
        current_likes=current_likes-1
    post.likes=current_likes
    post.save()
    return redirect(reverse('home'))

def favorite(req,post_id):
    user=req.user
    post=Post.objects.get(id=post_id)
    profile=Profile.objects.get(user=user)
    if profile.favorite.filter(id=post_id).exists():
        profile.favorite.remove(post)
    else:
        profile.favorite.add(post)
    return redirect(reverse('home'))

def favoritepostlist(req):
    user=req.user
    profile=user.profile
    favorite_post=profile.favorite.all()

    return render(req,'favoritepost.html',{'favorite_post':favorite_post})
def follow_user(req,user_id):
    user=req.user
    profile=Profile.objects.get(user=user)
    follow=Profile.objects.get(user=user_id)
    if profile.following.filter(user=user_id).exists():
        profile.following.remove(follow)
    else:
        profile.following.add(follow)
    return redirect('profile')

def following_users(req):
    user=req.user
    profile=Profile.objects.get(user=user)
    following=profile.following.all()
    return render(req,'Follow.html',{'following':following})

def follower_list(req):
    user=req.user
    profile=Profile.objects.get(user=user)
    follower=profile.follower.all()
    return render(req,'FollowerList.html',{'follower':follower})
