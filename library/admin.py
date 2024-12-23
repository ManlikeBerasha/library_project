from django.contrib import admin
from django.utils.html import format_html
from .models import Book, Author, Member, BorrowRecord, Category

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'books_count')
    search_fields = ('name', 'email')
    ordering = ('name',)
    
    def books_count(self, obj):
        return obj.get_books_count()
    books_count.short_description = 'Number of Books'

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'status_badge', 'category', 'available_copies')
    list_filter = ('status', 'category', 'authors')
    search_fields = ('title', 'isbn', 'authors__name')
    filter_horizontal = ('authors',)
    
    def status_badge(self, obj):
        colors = {
            'available': 'green',
            'borrowed': 'orange',
            'maintenance': 'red'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'membership_number', 'membership_status', 'date_joined')
    list_filter = ('membership_status', 'date_joined')
    search_fields = ('user__first_name', 'user__last_name', 'membership_number')

@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('book', 'member', 'borrow_date', 'due_date', 'return_status')
    list_filter = ('borrow_date', 'due_date', 'return_date')
    search_fields = ('book__title', 'member__user__first_name', 'member__user__last_name')
    
    def return_status(self, obj):
        if obj.return_date:
            return format_html('<span style="color: green;">Returned</span>')
        if obj.is_overdue:
            return format_html('<span style="color: red;">Overdue</span>')
        return format_html('<span style="color: orange;">On Loan</span>')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

# library/urls.py
from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='author-list'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('my-books/', views.MyBooksView.as_view(), name='my-books'),
    path('borrow/<int:pk>/', views.borrow_book, name='borrow-book'),
    path('return/<int:pk>/', views.return_book, name='return-book'),
]