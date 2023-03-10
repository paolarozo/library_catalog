"""
View for the book APIs
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Book
from book import serializers


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.BookSerializer
    queryset = Book.objects.all()
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

