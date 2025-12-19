from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from .models import *


def index(request):
    posts = Post.objects.all().order_by("-timestamp")
    paginator = Paginator(posts, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "pagination": paginator.num_pages > 1,
        "index": True,
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
    else:
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
    else:
        return render(request, "network/register.html")
    

@login_required
def new_post(request):
    """
    Create a new post
    """
    if request.method == "POST":
        content = request.POST.get("content").strip()
        p = Post(
            poster=request.user,
            content=content,
        )
        p.save()
        return HttpResponseRedirect(reverse("index"))


def profile(request, id):
    """
    Return profile of a user
    """
    profile = User.objects.get(pk=int(id))
    posts = profile.posts.order_by("-timestamp").all()
    paginator = Paginator(posts, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "username": profile.username,
        "id": profile.id,
        "post_count": len(posts),
        "following_count": profile.following_count(),
        "followers_count": profile.followers_count(),
        "page_obj": page_obj,
        "pagination": paginator.num_pages > 1,
        "followed": True if request.user.is_authenticated and profile in request.user.following.all() else False,
        "profile_info": True,
    })

@login_required
def follow(request):
    if request.method == "POST":
        user = User.objects.get(pk=int(request.POST.get("profile_id")))
        visitor = request.user
        if visitor in user.followers.all():
            user.followers.remove(visitor)
        else:
           user.followers.add(visitor) 
        user.save()
    return HttpResponseRedirect(reverse("profile", args=(user.id,)))

@login_required
def following(request):
    user = request.user
    posts = Post.objects.filter(poster__in=user.following.all()).order_by("-timestamp")

    paginator = Paginator(posts, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "pagination": paginator.num_pages > 1,
        "following_header": True,
    })

@csrf_exempt
@login_required
def posts(request, post_id):
    """
    API for updating the likes/content of a post
    """
    # Query for requested post
    try:
        post = Post.objects.get(pk=int(post_id))
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)
    
    if request.method == "GET":
        return JsonResponse(post.serialize())
    
    if request.method == "PUT":
        data = json.loads(request.body)
        # Update content of post after checking that the editor is the post creator
        if data.get("content") is not None and request.user.id == post.poster.id:
            post.content = data["content"]
            
        # Update post likes
        if data.get("like") is not None:
            if request.user not in post.likes.all():
                post.likes.add(request.user)
            else:
                post.likes.remove(request.user)   
        post.save()
        return JsonResponse(post.serialize())
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)
