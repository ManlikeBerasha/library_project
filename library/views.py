# library/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q
from .models import Book, Author, BorrowRecord, Member, Category
from .forms import BookSearchForm, BorrowBookForm

class HomeView(TemplateView):
    template_name = 'library/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'available_books_count': Book.objects.filter(status='available').count(),
            'authors_count': Author.objects.count(),
            'categories_count': Category.objects.count(),
            'recent_books': Book.objects.order_by('-created_at')[:5]
        })
        
        if self.request.user.is_authenticated:
            context['borrowed_books_count'] = BorrowRecord.objects.filter(
                member__user=self.request.user,
                return_date__isnull=True
            ).count()
        return context

class BookListView(ListView):
    model = Book
    template_name = 'library/book_list.html'
    context_object_name = 'books'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Book.objects.all().select_related('category').prefetch_related('authors')
        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        status = self.request.GET.get('status')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(authors__name__icontains=query) |
                Q(isbn__icontains=query)
            ).distinct()
            
        if category:
            queryset = queryset.filter(category__id=category)
            
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_form'] = BookSearchForm(self.request.GET)
        return context

class BookDetailView(DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['has_borrowed'] = BorrowRecord.objects.filter(
                book=self.object,
                member__user=self.request.user,
                return_date__isnull=True
            ).exists()
            context['borrow_form'] = BorrowBookForm()
        context['similar_books'] = Book.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:4]
        return context

class AuthorListView(ListView):
    model = Author
    template_name = 'library/author_list.html'
    context_object_name = 'authors'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Author.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset

class AuthorDetailView(DetailView):
    model = Author
    template_name = 'library/author_detail.html'
    context_object_name = 'author'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = self.object.books.all()
        return context

class MyBooksView(LoginRequiredMixin, ListView):
    template_name = 'library/my_books.html'
    context_object_name = 'borrow_records'
    
    def get_queryset(self):
        return BorrowRecord.objects.filter(
            member__user=self.request.user
        ).select_related('book').order_by('-borrow_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_loans'] = self.get_queryset().filter(return_date__isnull=True)
        context['return_history'] = self.get_queryset().filter(return_date__isnull=False)
        return context

@login_required
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BorrowBookForm(request.POST)
        if form.is_valid():
            if not book.is_available():
                messages.error(request, 'This book is not available for borrowing.')
                return redirect('library:book-detail', pk=pk)
            
            try:
                member = Member.objects.get(user=request.user)
            except Member.DoesNotExist:
                messages.error(request, 'You need to be a registered member to borrow books.')
                return redirect('library:book-detail', pk=pk)
            
            # Check if user has already borrowed this book
            existing_borrow = BorrowRecord.objects.filter(
                book=book,
                member=member,
                return_date__isnull=True
            ).exists()
            
            if existing_borrow:
                messages.error(request, 'You have already borrowed this book.')
                return redirect('library:book-detail', pk=pk)
            
            # Create borrow record
            BorrowRecord.objects.create(
                book=book,
                member=member,
                due_date=timezone.now() + timezone.timedelta(days=14)
            )
            
            messages.success(request, f'Successfully borrowed {book.title}')
            return redirect('library:my-books')
    
    return redirect('library:book-detail', pk=pk)

@login_required
def return_book(request, pk):
    borrow_record = get_object_or_404(
        BorrowRecord,
        pk=pk,
        member__user=request.user,
        return_date__isnull=True
    )
    
    if request.method == 'POST':
        borrow_record.return_date = timezone.now()
        borrow_record.save()
        
        book = borrow_record.book
        book.available_copies += 1
        if book.available_copies > 0:
            book.status = 'available'
        book.save()
        
        messages.success(request, f'Successfully returned {book.title}')
    
    return redirect('library:my-books')

@login_required
def extend_borrow(request, pk):
    borrow_record = get_object_or_404(
        BorrowRecord,
        pk=pk,
        member__user=request.user,
        return_date__isnull=True
    )
    
    if not borrow_record.is_overdue:
        borrow_record.due_date += timezone.timedelta(days=7)
        borrow_record.save()
        messages.success(request, f'Successfully extended borrowing period for {borrow_record.book.title}')
    else:
        messages.error(request, 'Cannot extend overdue books. Please return the book first.')
    
    return redirect('library:my-books')

class CategoryListView(ListView):
    model = Category
    template_name = 'library/category_list.html'
    context_object_name = 'categories'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for category in context['categories']:
            category.book_count = category.books.count()
        return context