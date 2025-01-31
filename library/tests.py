from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Author, Book, Member, BorrowRecord, Librarian
from django.contrib.auth.models import User

class AuthorTests(APITestCase):
    def test_create_author(self):
        url = reverse('author-list')
        data = {'first_name': 'John', 'last_name': 'Doe'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_authors(self):
        url = reverse('author-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_author(self):
        author = Author.objects.create(first_name='John', last_name='Doe')
        url = reverse('author-detail', args=[author.id])
        data = {'first_name': 'Jane', 'last_name': 'Doe'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_author(self):
        author = Author.objects.create(first_name='John', last_name='Doe')
        url = reverse('author-detail', args=[author.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT
                        )


class BookTests(APITestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name='John', last_name='Doe')

    def test_create_book(self):
        url = reverse('book-list')
        data = {'title': 'Sample Book', 'author': self.author.id, 'isbn': '1234567890123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_books(self):
        url = reverse('book-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_book(self):
        book = Book.objects.create(title='Sample Book', author=self.author, isbn='1234567890123')
        url = reverse('book-detail', args=[book.id])
        data = {'title': 'Updated Book', 'author': self.author.id, 'isbn': '1234567890123'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_book(self):
        book = Book.objects.create(title='Sample Book', author=self.author, isbn='1234567890123')
        url = reverse('book-detail', args=[book.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class MemberTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.member = Member.objects.create(user=self.user, address='123 Main St', phone_number='1234567890')

    def test_create_member(self):
        new_user = User.objects.create_user(username='newuser', password='newpassword')
        url = reverse('member-list')
        data = {'user': new_user.id, 'address': '123 Main St', 'phone_number': '1234567890'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_members(self):
        url = reverse('member-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_member(self):
        url = reverse('member-detail', args=[self.member.id])
        data = {'user': self.user.id, 'address': '456 Elm St', 'phone_number': '0987654321'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_member(self):
        url = reverse('member-detail', args=[self.member.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class BorrowRecordTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.member = Member.objects.create(user=self.user, address='123 Main St', phone_number='1234567890')
        self.author = Author.objects.create(first_name='John', last_name='Doe')
        self.book = Book.objects.create(title='Sample Book', author=self.author, isbn='1234567890123')
        self.borrow_record = BorrowRecord.objects.create(member=self.member, book=self.book)

    def test_create_borrow_record(self):
        url = reverse('borrowrecord-list')
        data = {'member': self.member.id, 'book': self.book.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_borrow_records(self):
        url = reverse('borrowrecord-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_borrow_record(self):
        url = reverse('borrowrecord-detail', args=[self.borrow_record.id])
        data = {'member': self.member.id, 'book': self.book.id, 'is_returned': True}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_borrow_record(self):
        url = reverse('borrowrecord-detail', args=[self.borrow_record.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class LibrarianTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.librarian = Librarian.objects.create(user=self.user, employee_id='EMP001', phone_number='1234567890')

    def test_create_librarian(self):
        new_user = User.objects.create_user(username='newuser', password='newpassword')
        url = reverse('librarian-list')
        data = {'user': new_user.id, 'employee_id': 'EMP002', 'phone_number': '0987654321'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_librarians(self):
        url = reverse('librarian-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_librarian(self):
        url = reverse('librarian-detail', args=[self.librarian.id])
        data = {'user': self.user.id, 'employee_id': 'EMP003', 'phone_number': '1122334455'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_librarian(self):
        url = reverse('librarian-detail', args=[self.librarian.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)