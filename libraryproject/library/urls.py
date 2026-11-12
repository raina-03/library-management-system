
from django.urls import path
from . import views

urlpatterns = [
    path("admin-login/", views.admin_login, name="admin_login"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-logout/", views.admin_logout, name="admin_logout"),

    path("add-book/", views.add_book, name="add_book"),
    path("update-book/<int:book_id>/", views.update_book, name="update_book"),
    path("delete-book/<int:book_id>/", views.delete_book, name="delete_book"),
    path("register/", views.register, name="register"),
    path("user-login/", views.user_login, name="user_login"),
    path("books/", views.book_list, name="book_list"),
    path("user-logout/", views.user_logout, name="user_logout"),
    path("rent/<int:book_id>/", views.rent_book, name="rent_book"),
    path("my-rentals/", views.my_rentals, name="my_rentals"),
    path("return-book/<int:rental_id>/", views.return_book, name="return_book"),
    path("admin-rentals/", views.admin_rentals, name="admin_rentals"),
    path("", views.home, name="home"),
]   
