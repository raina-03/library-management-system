
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta



class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title



class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    rental_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)

    rental_fee = models.DecimalField(
        max_digits=8, decimal_places=2, default=20
    )
    fine_per_day = models.DecimalField(
        max_digits=6, decimal_places=2, default=5
    )

    def save(self, *args, **kwargs):
        if self.due_date is None:
            self.due_date = self.rental_date + timedelta(days=7)
        super().save(*args, **kwargs)

    @property
    def fine(self):
        end_date = self.return_date or timezone.localdate()
        overdue_days = max((end_date - self.due_date).days, 0)
        return overdue_days * self.fine_per_day

    @property
    def is_returned(self):
        return self.return_date is not None

    def __str__(self):
        return f"{self.book.title} - {self.user.username}"
    

