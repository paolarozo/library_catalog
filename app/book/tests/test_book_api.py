"""
Test for book APIS
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Book

from book.serializers import BookSerializer
import datetime

BOOKS_URL = reverse('book:book-list')


def detail_url(book_id):
    return reverse('book:book-detail', args=[book_id])

def create_book(user, **params):
    defaults = {
        'title': 'Sample book',
        'author': 'Sample Author',
        'publication_date': datetime.date(1997, 10, 19)
    }
    defaults.update(params)

    book = Book.objects.create(user=user, **defaults)
    return book


class PublicBookAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBookAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@test.com',
            'pass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_books(self):
        create_book(user=self.user)
        create_book(user=self.user)

        res = self.client.get(BOOKS_URL)
        books = Book.objects.all().order_by('id')
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book(self):
        payload = {
            'title': 'Sample book two',
            'author': 'Sample Author two',
            'publication_date': datetime.date(1995, 10, 19)
        }
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(book, k), v)

        self.assertEqual(book.user, self.user)

    def test_partial_update_book(self):
        original_author = 'Test Author'
        book = create_book(
            user=self.user,
            title='Test title',
            author=original_author,
            publication_date=datetime.date(1997, 10, 19)
        )

        payload = {'title': 'New title'}
        url = detail_url(book.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.title, payload['title'])
        self.assertEqual(book.author, original_author)

    def test_delete_book(self):
        """Test deleting a recipe successful."""
        book = create_book(user=self.user)

        url = detail_url(book.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())

