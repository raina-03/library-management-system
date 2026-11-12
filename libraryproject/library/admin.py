
from django.contrib import admin
from .models import Book, Rental


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'total_copies',
        'available_copies',
    )
    search_fields = ('title', 'author')


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'book',
        'rental_date',
        'due_date',
        'return_date',
        'rental_fee',
    )
    list_filter = ('rental_date', 'due_date', 'return_date')

