from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user/<int:user_id>/page/<int:page_no>", views.user_profile, name="user_profile"),
    path("follow/<int:user_id>", views.toggle_follow, name="toggle_follow"),
    path("following/<int:page_id>", views.following_feed, name="following_feed"),
    path("edit/<int:post_id>", views.update_post, name="update_post"),
    path("new-post", views.create_post, name="create-post"),
    path("new_post", views.new_post, name="new-post"),
    path("like/<int:post_id>", views.toggle_like, name="toggle-like"),
    path("page/<int:page_no>", views.load_page, name="load_page"),
]
