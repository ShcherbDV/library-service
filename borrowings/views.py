from rest_framework import generics

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer


class BorrowingListView(generics.ListAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BorrowingDetailView(generics.RetrieveAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
