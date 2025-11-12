from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingCreateSerializer, BorrowingReturnSerializer


class BorrowingListView(generics.ListCreateAPIView):

    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BorrowingCreateSerializer
        return BorrowingSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Borrowing.objects.all()

        if not user.is_staff:
            queryset = queryset.filter(user=user)
        else:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user__id=user_id)

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(actual_return_date=False)

        return queryset.order_by("-borrow_date")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BorrowingDetailView(generics.RetrieveAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)


class BorrowingReturnView(generics.UpdateAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReturnSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        borrowing = get_object_or_404(Borrowing, pk=self.kwargs["pk"])
        user = self.request.user
        if not user.is_staff and borrowing.user != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only return your own borrowings.")
        return borrowing

    def perform_update(self, serializer):
        borrowing = serializer.instance

        if borrowing.actual_return_date:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("This borrowing has already been returned.")

        borrowing.actual_return_date = timezone.now().date()
        borrowing.save()

        borrowing.book.inventory += 1
        borrowing.book.save()
