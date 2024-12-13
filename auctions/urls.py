from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("categories/", views.category, name="category"),
    path("category/<str:category>", views.items_in_category, name="items_in_category"),
    path("comment/<int:item_id>", views.comment, name="comment"),
    path("itemclosed/<int:item_id>", views.close_item, name="itemclose"),
    path("add/<int:item_id>", views.add_watchlist, name="add_watchlist"),
    path("remove/<int:item_id>", views.remove_watchlist, name="remove_watchlist"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("item/<int:item_id>", views.item, name="item")
]


