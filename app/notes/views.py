from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, filters
from django_filters import rest_framework as df_filters
from .serializers import UserSerializer, NoteSerializer
from .models import Note


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    # TODO: Right now, all authenticated users can create and update users.
    # This should only be available for admins.

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
    filter_backends = [filters.SearchFilter, df_filters.DjangoFilterBackend]
    search_fields = ["title", "body"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        # TODO: By default, notes are ordered by insertion order. It would
        # probably make sense to introduce created_at/updated_at fields and
        # use them for ordering.
        return Note.objects.filter(author=self.request.user)
