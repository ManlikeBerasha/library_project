from rest_framework import serializers
from .models import Author, Book, Member, BorrowRecord, Librarian
from django.contrib.auth.models import User

# Author serializer
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'date_of_birth', 'date_of_death']

    # Custom validation for first_name and last_name
    def validate_first_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("First name should contain only alphabetic characters.")
        return value

    def validate_last_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("Last name should contain only alphabetic characters.")
        return value

# Book serializer
class BookSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), write_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'genre', 'description', 'published_date', 'total_copies', 'available_copies']

    # Custom validation for ISBN
    def validate_isbn(self, value):
        if len(value) != 13:
            raise serializers.ValidationError("ISBN must be 13 characters long.")
        return value

# Member serializer
class MemberSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Member
        fields = ['id', 'user', 'address', 'phone_number', 'membership_date']

    # Custom validation for phone number
    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        if len(value) not in [10, 15]:  # Modify the length based on your country's phone number format
            raise serializers.ValidationError("Phone number must be 10 or 15 digits long.")
        return value

# BorrowRecord serializer
class BorrowRecordSerializer(serializers.ModelSerializer):
    member = serializers.PrimaryKeyRelatedField(queryset=Member.objects.all(), write_only=True)
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True)

    class Meta:
        model = BorrowRecord
        fields = ['id', 'member', 'book', 'borrow_date', 'return_date', 'is_returned']

    # Custom validation for return date
    def validate(self, data):
        if data.get('is_returned') and not data.get('return_date'):
            raise serializers.ValidationError("Return date is required if the book is returned.")
        return data

# Librarian serializer
class LibrarianSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Librarian
        fields = ['id', 'user', 'employee_id', 'hire_date', 'phone_number']

    # Custom validation for employee_id and phone_number
    def validate_employee_id(self, value):
        if not value.isalnum():
            raise serializers.ValidationError("Employee ID should be alphanumeric.")
        return value

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        return value