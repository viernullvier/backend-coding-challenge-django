import uuid
from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.SlugField(primary_key=True, max_length=64)

    def __str__(self):
        return self.name


class Note(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name="notes", blank=True)

    def __str__(self):
        return f"{self.title} [{self.author.username}]"
