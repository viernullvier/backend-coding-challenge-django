from django.contrib.auth.models import User
from rest_framework import viewsets, filters
from django_filters import rest_framework as df_filters
from django.db.models import Q
from .serializers import UserSerializer, NoteSerializer
from .models import Note
from .permissions import IsAuthenticatedOrPublic, IsSelf


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [IsSelf]


class NoteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows notes to be viewed or edited.
    """

    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticatedOrPublic]
    filterset_fields = ["tags", "public"]
    filter_backends = [filters.SearchFilter, df_filters.DjangoFilterBackend]
    search_fields = ["title", "body"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        # TODO: By default, notes are ordered by insertion order. It would
        # probably make sense to introduce created_at/updated_at fields and
        # use them for ordering.
        if not self.request.user.is_authenticated:
            return Note.objects.filter(public=True)
        return Note.objects.filter(
            Q(author=self.request.user) | Q(public=True)
        )
