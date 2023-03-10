"""
Serializers for book APIS
"""

from rest_framework import serializers
from core.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'publication_date']
        read_only_fields = ['id']