from rest_framework import serializers

from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active",
        )
        read_only_fields = ["borrow_date", "user", "is_active"]


class BorrowingCreateSerializer(BorrowingSerializer):

    def validate(self, attrs):
        book = self.attrs.get("book")

        if book.inventory <= 0:
            raise serializers.ValidationError(
                {"book": "This book is currently out of stock!"}
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        book = validated_data.pop("book")

        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.create(user=request.user, **validated_data)
        return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active",
        )
        read_only_fields = [
            "borrow_date",
            "user",
            "is_active",
            "id",
            "book",
            "is_active",
            "expected_return_date",
            "actual_return_date",
        ]

        def validate(self, attrs):
            borrowing = self.instance
            if borrowing.actual_return_date is not None:
                raise serializers.ValidationError(
                    "This borrowing has already been returned"
                )
            return attrs
