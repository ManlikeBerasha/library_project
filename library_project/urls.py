from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='author-list'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('my-books/', views.MyBooksView.as_view(), name='my-books'),
    path('borrow/<int:pk>/', views.borrow_book, name='borrow-book'),
    path('return/<int:pk>/', views.return_book, name='return-book'),
    path('extend/<int:pk>/', views.extend_borrow, name='extend-borrow'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
]