from django.db import models


Cover = models.TextChoices("Cover", "HARD SOFT")

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.CharField(choices=Cover)
    inventory = models.IntegerField()
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]
