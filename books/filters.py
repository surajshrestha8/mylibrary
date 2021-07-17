import django_filters
from .models import *
from users.models import Student

class BookFilter(django_filters.FilterSet):
    class Meta:
        model = Book
        fields = '__all__'
        exclude = ['is_available']


class StudentFilter(django_filters.FilterSet):
    class Meta:
        model = Borrower
        fields = '__all__'

