from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from django_filters import rest_framework as df_filters
from .serializers import UserSerializer, NoteSerializer
from .models import Note


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class NoteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows notes to be viewed or edited.
    """

    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["tags"]
    filter_backends = [df_filters.DjangoFilterBackend]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        return Note.objects.filter(author=self.request.user)
