from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("listings/<int:id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("bid", views.bid, name="bid"),
    path("close", views.close, name="close"),
    path("categories", views.categories, name="categories"),
    path("results", views.results, name="results"),
    path("comment", views.comment, name="comment"),
    path("users/<int:id>", views.users, name="users"),
]
