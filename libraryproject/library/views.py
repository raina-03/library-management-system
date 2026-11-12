
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST
from .models import Book
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from .models import Book, Rental


def home(request):
    return render(request, "library/home.html")




def admin_check(user):
    return user.is_authenticated and user.is_staff



def admin_login(request):
    error = ""

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_staff:
            login(request, user)
            return redirect("admin_dashboard")
        else:
            error = "Invalid admin username or password."

    return render(
        request,
        "library/admin_login.html",
        {"error": error}
    )



@user_passes_test(admin_check, login_url="/admin-login/")
def admin_dashboard(request):
    books = Book.objects.all()
    return render(
        request,
        "library/admin_dashboard.html",
        {"books": books}
    )



def admin_logout(request):
    if request.method == "POST":
        if request.user.is_authenticated and request.user.is_staff:
            logout(request)

    return redirect("admin_login")


@user_passes_test(admin_check, login_url="/admin-login/")
def add_book(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "").strip()

        try:
            total_copies = int(request.POST.get("total_copies", "1"))
        except ValueError:
            total_copies = 0

        if title and author and total_copies > 0:
            Book.objects.create(
                title=title,
                author=author,
                total_copies=total_copies,
                available_copies=total_copies
            )
            return redirect("admin_dashboard")

        return render(request, "library/add_book.html", {
            "error": "Enter valid book details."
        })

    return render(request, "library/add_book.html")



@user_passes_test(admin_check, login_url="/admin-login/")
def update_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "").strip()

        try:
            total_copies = int(request.POST.get("total_copies", "0"))
        except ValueError:
            total_copies = 0

        borrowed = book.total_copies - book.available_copies

        if title and author and total_copies >= borrowed and total_copies > 0:
            book.title = title
            book.author = author
            book.total_copies = total_copies
            book.available_copies = total_copies - borrowed
            book.save()
            return redirect("admin_dashboard")

        return render(request, "library/update_book.html", {
            "book": book,
            "error": "Enter valid details and enough copies for current rentals."
        })

    return render(request, "library/update_book.html", {"book": book})



@user_passes_test(admin_check, login_url="/admin-login/")
@require_POST
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if book.available_copies == book.total_copies:
        book.delete()

    return redirect("admin_dashboard")

def register(request):
    error = ""

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not all([full_name, username, email, password, confirm_password]):
            error = "Please fill in all fields."

        elif password != confirm_password:
            error = "Passwords do not match."

        elif User.objects.filter(username=username).exists():
            error = "Username already exists."

        elif User.objects.filter(email__iexact=email).exists():
            error = "Email already registered."

        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=full_name
            )
            return redirect("user_login")

    return render(request, "library/register.html", {"error": error})


def user_login(request):
    error = ""

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and not user.is_staff:
            login(request, user)
            return redirect("book_list")
        else:
            error = "Invalid user username or password."

    return render(
        request,
        "library/user_login.html",
        {"error": error}
    )


@login_required(login_url="/user-login/")
def book_list(request):
    if request.user.is_staff:
        return redirect("admin_dashboard")

    books = Book.objects.all().order_by("title")

    return render(
        request,
        "library/book_list.html",
        {"books": books}
    )


@login_required(login_url="/user-login/")
def user_logout(request):
    if request.method == "POST" and not request.user.is_staff:
        logout(request)

    return redirect("user_login")


@login_required(login_url="/user-login/")
def rent_book(request, book_id):
    if request.user.is_staff:
        return redirect("admin_dashboard")

    if request.method != "POST":
        return redirect("book_list")

    with transaction.atomic():
        book = get_object_or_404(
            Book.objects.select_for_update(),
            id=book_id
        )

        if book.available_copies < 1:
            messages.error(request, "Sorry, this book is unavailable.")
        else:
            active_rental = Rental.objects.filter(
                user=request.user,
                book=book,
                return_date__isnull=True
            ).exists()

            if active_rental:
                messages.warning(
                    request,
                    "You have already rented this book."
                )
            else:
                Rental.objects.create(
                    user=request.user,
                    book=book,
                    rental_date=timezone.localdate(),
                    rental_fee=20,
                    fine_per_day=5
                )

                book.available_copies -= 1
                book.save(update_fields=["available_copies"])

                messages.success(
                    request,
                    f"You rented {book.title} successfully!"
                )

    return redirect("book_list")


@login_required(login_url="/user-login/")
def return_book(request, rental_id):
    if request.method != "POST":
        return redirect("my_rentals")

    if request.user.is_staff:
        return redirect("admin_dashboard")

    with transaction.atomic():
        rental = get_object_or_404(
            Rental.objects.select_for_update().select_related("book"),
            id=rental_id,
            user=request.user,
            return_date__isnull=True
        )

        rental.return_date = timezone.localdate()
        rental.save(update_fields=["return_date"])

        book = Book.objects.select_for_update().get(
            id=rental.book_id
        )
        book.available_copies += 1
        book.save(update_fields=["available_copies"])

    return redirect("my_rentals")

@login_required(login_url="/user-login/")
def my_rentals(request):
    if request.user.is_staff:
        return redirect("admin_dashboard")

    rentals = Rental.objects.filter(
        user=request.user
    ).select_related("book").order_by("-rental_date", "-id")

    return render(
        request,
        "library/my_rentals.html",
        {"rentals": rentals}
    )

@user_passes_test(admin_check, login_url="/admin-login/")
def admin_rentals(request):
    rentals = Rental.objects.select_related(
        "user", "book"
    ).order_by("-rental_date", "-id")

    return render(
        request,
        "library/admin_rentals.html",
        {"rentals": rentals}
    )
