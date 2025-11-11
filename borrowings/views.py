from rest_framework import generics

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingCreateSerializer


class BorrowingListView(generics.ListCreateAPIView):
    queryset = Borrowing.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BorrowingCreateSerializer
        return BorrowingSerializer


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BorrowingDetailView(generics.RetrieveAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
