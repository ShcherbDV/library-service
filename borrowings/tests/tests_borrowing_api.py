from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer

BORROWING_URL = reverse("borrowings:borrowing-list")

def sample_book(**params):
    defaults = {
        "title": "Witcher",
        "author": "Andrzej Sapkowski",
        "cover": "HARD",
        "inventory": 10,
        "daily_fee": 2.55,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)

def sample_borrowing(**params):
    book = sample_book()
    user = params.pop("user", None)
    if user is None:
        user = get_user_model().objects.create_user(email=f"test_{Book.objects.count()}@mail.com", password="password")

    defaults = {
        "borrow_date": "2025-06-02",
        "expected_return_date": "2025-07-02",
        "actual_return_date": "2025-08-02",
        "book": book,
        "user": user,
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)

def detail_url(borrowing_id):
    return reverse("borrowings:borrowing-detail", args=[borrowing_id])


class AuthenticatedBorrowingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com", password="password"
        )
        self.client.force_authenticate(self.user)

    def test_borrowing_list(self):
        sample_borrowing(user=self.user)

        res = self.client.get(BORROWING_URL)
        borrowings = Borrowing.objects.all()
        serializer = BorrowingSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_borrowings_by_user_id(self):
        borrowing = sample_borrowing()
        borrowing_with_another_user = sample_borrowing()

        res = self.client.get(BORROWING_URL, {"user_id": f"{self.user.id}"})

        serializer = BorrowingSerializer(borrowing)
        serializer_with_another_user = BorrowingSerializer(borrowing_with_another_user)

        self.assertIn(serializer_with_another_user.data, res.data)
        self.assertNotIn(serializer.data, res.data)

    def test_filter_borrowings_is_active(self):
        borrowing = sample_borrowing()
        borrowing_with_is_active = sample_borrowing(actual_return_date=None)

        res = self.client.get(BORROWING_URL, {"is_active": f"{borrowing_with_is_active.is_active}"})

        serializer = BorrowingSerializer(borrowing)
        serializer_with_is_active = BorrowingSerializer(borrowing_with_is_active)

        self.assertIn(serializer_with_is_active.data, res.data)
        self.assertNotIn(serializer.data, res.data)

    def test_retrieve_borrowing_detail(self):
        borrowing = sample_borrowing()

        url = detail_url(borrowing.id)

        res = self.client.get(url)

        serializer = BorrowingSerializer(borrowing)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AdminMovieAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@mail.com", password="password", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_borrowing(self):
        book = sample_book()

        payload = {
            "expected_return_date": "2025-07-02",
            "actual_return_date": "2025-08-02",
            "book": book.id,
            "user": self.user.id,
        }

        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
