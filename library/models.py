# library/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True, blank=True, null=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_books_count(self):
        return self.books.count()

class Book(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('maintenance', 'Under Maintenance')
    ]
    
    title = models.CharField(max_length=200)
    isbn = models.CharField('ISBN', max_length=13, unique=True)
    category = models.ForeignKey(Category, related_name='books', on_delete=models.SET_NULL, null=True)
    authors = models.ManyToManyField(Author, related_name='books')
    description = models.TextField()i
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

    def is_available(self):
        return self.status == 'available' and self.available_copies > 0

class Member(models.Model):
    MEMBERSHIP_CHOICES = [
        ('regular', 'Regular'),
        ('premium', 'Premium'),
        ('suspended', 'Suspended')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership_number = models.CharField(max_length=10, unique=True)
    membership_status = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES, default='regular')
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.membership_number})"

    @property
    def full_name(self):
        return self.user.get_full_name()

class BorrowRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.book.title} - {self.member.full_name}"

    @property
    def is_overdue(self):
        return not self.return_date and timezone.now() > self.due_date

    def save(self, *args, **kwargs):
        if not self.pk:  # New record
            if not self.due_date:
                self.due_date = timezone.now() + timedelta(days=14)
            self.book.available_copies -= 1
            if self.book.available_copies == 0:
                self.book.status = 'borrowed'
            self.book.save()
        super().save(*args, **kwargs)