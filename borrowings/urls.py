from django.urls import path

from borrowings.views import BorrowingListView, BorrowingDetailView, BorrowingReturnView

app_name = "borrowings"


urlpatterns = [
    path("", BorrowingListView.as_view(), name="borrowing-list"),
    path("<int:pk>/", BorrowingDetailView.as_view(), name="borrowing-detail"),
    path("<int:pk>/return/", BorrowingReturnView.as_view(), name="borrowing-return"),
]
