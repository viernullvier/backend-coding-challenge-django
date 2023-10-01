from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Note, Tag


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email"]


class NoteSerializer(serializers.HyperlinkedModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field="name",
        queryset=Tag.objects.all(),
        allow_null=True,
    )
    author = serializers.HyperlinkedRelatedField(
        view_name="user-detail", read_only=True
    )

    class Meta:
        model = Note
        fields = ["url", "title", "body", "tags", "author"]

    def to_internal_value(self, data):
        # This will ensure that nonexistent tags are created when adding or
        # updating notes.
        # FIXME: This code will run _before_ validation. Requests that fail
        # validation will still generate new tag entries, enabling attackers
        # to spam the database.
        tags = data.get("tags", [])
        if isinstance(tags, str):
            tag = Tag.objects.get_or_create(name=tags)
        else:
            for tag in tags:
                tag = Tag.objects.get_or_create(name=tag)
        return super().to_internal_value(data)
