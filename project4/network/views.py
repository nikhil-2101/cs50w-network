import json
from django import http
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import User, Posts, Like, Follow


def index(request):
    posts = paginate_posts(1)
    liked_posts = get_liked_posts(posts, request.user)
    return render(request, "network/index.html", {
        "posts": posts,
        "liked_posts": liked_posts,
        "pages": "page"
    })

def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "network/register.html")


def get_liked_posts(posts, user):
    liked_posts = [post.id for post in posts if user in post.liked_usr.all()]
    return liked_posts


def paginate_posts(page_id):
    posts = Posts.objects.all().order_by('-time')
    paginator = Paginator(posts, 10)
    return paginator.get_page(page_id)

def create_post(request):
    if request.method == "POST":
        Posts.objects.create(user=request.user, content=request.POST["content"])
        return HttpResponseRedirect(reverse('index'))
    return HttpResponse("Error: This page only accepts post requests")

@csrf_exempt
def toggle_like(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Posts, pk=post_id)
        like, created = Like.objects.get_or_create(post=post)
        if request.user in like.liked_users.all():
            like.liked_users.remove(request.user)
            action = "u"
        else:
            like.liked_users.add(request.user)
            action = "l"
        post.like = like.liked_users.count()
        post.save()
        return JsonResponse({
            "stat": "Success",
            "likes": post.like,
            "action": action
        }, status=200)
    return HttpResponse("This page only accepts POST requests")

@csrf_exempt
def user_profile(request, user_id, page_no):
    usr = get_object_or_404(User, pk=user_id)
    follow_data = usr.follows.first()
    
    if request.method == "POST":
        toggle_follow(request.user, usr, follow_data)
        action = "Unfollow" if request.user in follow_data.followers.all() else "Follow"
        return JsonResponse({
            "stat": action,
            "followers": follow_data.followers.count(),
            "following": follow_data.followed_users.count()
        }, status=200)

    posts = usr.user_posts.all().order_by("-time")
    paginator = Paginator(posts, 10)
    posts = paginator.page(page_no)
    liked_posts = get_liked_posts(posts, request.user)
    
    followers_count = follow_data.followers.count()
    following_count = follow_data.followed_users.count()
    is_following = request.user in follow_data.followers.all()
    
    return render(request, "network/user.html", {
        "posts": posts,
        "liked_posts": liked_posts,
        "usr": usr,
        "followers": followers_count,
        "followings": following_count,
        "btnText": "Unfollow" if is_following else "Follow"
    })

def toggle_follow(usr_following, usr_followed, follow_data):
    if usr_following in follow_data.followers.all():
        follow_data.followers.remove(usr_following)
        usr_following.follows.first().followed_users.remove(usr_followed)
    else:
        follow_data.followers.add(usr_following)
        usr_following.follows.first().followed_users.add(usr_followed)

def following_feed(request, page_id):
    follower_instance, created = Follow.objects.get_or_create(user=request.user)
    followed_users = follower_instance.followed_users.all()
    
    posts = Paginator(Posts.objects.filter(user__in=followed_users).order_by("-time"), 10).get_page(page_id)
    liked_posts = get_liked_posts(posts, request.user)
    
    return render(request, "network/following_feed.html", {
        "posts": posts,
        "liked_posts": liked_posts,
        "pages": "following"
    })



@csrf_exempt
def update_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Posts, pk=post_id)
        if post.user != request.user:
            return JsonResponse({"stat": "Failed"}, status=404)
        data = json.loads(request.body).get("edited")
        post.post = data  # Ensure you're updating the correct field
        post.save()
        return JsonResponse({"stat": "Success", "post": post.post}, status=200) 
    return HttpResponse("This page only accepts POST requests")



def load_page(request, page_no):
    posts = paginate_posts(page_no)
    liked_posts = get_liked_posts(posts, request.user)
    return render(request, "network/index.html", {
        "posts": posts,
        "liked_posts": liked_posts,
        "pages": "page"
    })

def new_post(request):
    if request.method == "POST":
        content = request.POST.get("post")
        if content:
            Posts.objects.create(user=request.user, post=content)
            return redirect('index')
    return render(request, "network/new_post.html")