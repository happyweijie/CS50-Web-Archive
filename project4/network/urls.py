
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("profiles/<int:id>", views.profile, name="profile"),
    path("follow", views.follow, name="follow"),
    path("following", views.following, name="following"),

    # API Paths
    path("posts/<int:post_id>", views.posts, name="posts"),
]
