from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Note, Tag

HOST_URL = "http://testserver"


def url_for_note(note, include_host=False):
    # FIXME: Host URL is not evaluated at runtime, but hardcoded.
    # Might break in future dependency updates.
    url = reverse("note-detail", kwargs={"pk": note.id})
    if not include_host:
        return url
    return f"{HOST_URL}{url}"


def url_for_user(user, include_host=False):
    # FIXME: Host URL is not evaluated at runtime, but hardcoded.
    # Might break in future dependency updates.
    url = reverse("user-detail", kwargs={"pk": user.id})
    if not include_host:
        return url
    return f"{HOST_URL}{url}"


class NotesTestCase(TestCase):
    def assertDictContainsSubset(self, a, b):
        self.assertEqual(b, b | a)

    def setUp(self):
        # Fixtures: 2 users, 2 posts per user (1 tagged, 1 untagged)
        self.tag_1 = Tag.objects.create(name="tag1")
        self.tag_2 = Tag.objects.create(name="tag2")
        self.user_1 = User.objects.create(
            username="user1", email="user1@example.com"
        )
        self.note_1_1 = Note.objects.create(
            author=self.user_1, title="title1", body="body1"
        )
        self.note_1_2 = Note.objects.create(
            author=self.user_1, title="title2", body="body2"
        )
        self.note_1_2.tags.add(self.tag_1)
        self.user_2 = User.objects.create(
            username="user2", email="user2@example.com"
        )
        self.note_2_1 = Note.objects.create(
            author=self.user_2, title="title1", body="body1"
        )
        self.note_2_2 = Note.objects.create(
            author=self.user_2, title="title2", body="body2"
        )
        self.note_2_2.tags.add(self.tag_2)

        self.client = APIClient()

    def test_user_can_create_notes(self):
        self.client.force_authenticate(self.user_1)
        payload = {"title": "Hello world!", "body": "First note"}
        response = self.client.post("/notes/", payload)
        self.assertDictContainsSubset(payload, response.json())
        assert response.status_code == 201

    def test_user_can_tag_notes(self):
        self.client.force_authenticate(self.user_1)
        payload = {
            "title": "Hello again!",
            "body": "Second note",
            "tags": ["Hello", "Test"],
        }
        response = self.client.post("/notes/", payload)
        self.assertDictContainsSubset(payload, response.json())
        assert response.status_code == 201

    def test_user_can_list_notes(self):
        self.client.force_authenticate(self.user_1)
        response = self.client.get("/notes/")
        payload = response.json()
        assert len(payload) == 2
        for note in payload:
            self.assertIn("author", note)
            self.assertIn("title", note)
            self.assertIn("body", note)
            self.assertIn("tags", note)
            self.assertIn("url", note)
            assert note["author"] == url_for_user(self.user_1, True)
        assert response.status_code == 200

    def test_tag_gets_created_if_nonexistent(self):
        with self.assertRaises(Tag.DoesNotExist):
            tag = Tag.objects.get(name="new")
        self.client.force_authenticate(self.user_1)
        payload = {"title": "New tag", "body": "Second note", "tags": ["new"]}
        self.client.post("/notes/", payload)
        tag = Tag.objects.get(name="new")
        assert tag.name == "new"

    def test_user_can_patch_notes(self):
        self.client.force_authenticate(self.user_1)
        note_url = url_for_note(self.note_1_1)
        payload = {"title": "updated", "tags": ["new"]}
        response = self.client.patch(note_url, payload)
        note = response.json()
        assert note["title"] == "updated"
        self.assertEquals(note["tags"], payload["tags"])
        assert response.status_code == 200
        tag = Tag.objects.get(name="new")
        assert tag.name == "new"

    def test_user_can_put_notes(self):
        self.client.force_authenticate(self.user_1)
        note_url = url_for_note(self.note_1_1)
        payload = {"title": "updated", "body": "updated body", "tags": ["new"]}
        response = self.client.put(note_url, payload)
        note = response.json()
        assert note["title"] == "updated"
        assert note["body"] == "updated body"
        self.assertEquals(note["tags"], payload["tags"])
        assert response.status_code == 200
        tag = Tag.objects.get(name="new")
        assert tag.name == "new"

    def test_user_can_delete_notes(self):
        self.client.force_authenticate(self.user_1)
        note_url = url_for_note(self.note_1_1)
        response = self.client.delete(note_url)
        assert response.status_code == 204
        with self.assertRaises(Note.DoesNotExist):
            Note.objects.get(id=self.note_1_1.id)
        response = self.client.get("/notes/")
        payload = response.json()
        assert len(payload) == 1

    def test_user_can_filter_notes_by_tag(self):
        self.client.force_authenticate(self.user_1)
        response = self.client.get("/notes/?tags=tag1")
        payload = response.json()
        assert len(payload) == 1
        for note in payload:
            self.assertEquals(note["title"], self.note_1_2.title)
            self.assertEquals(note["body"], self.note_1_2.body)
            self.assertEquals(note["author"], url_for_user(self.user_1, True))
            self.assertEquals(note["tags"], ["tag1"])
        assert response.status_code == 200

        response = self.client.get("/notes/?tags=tag2")
        payload = response.json()
        assert len(payload) == 0
        assert response.status_code == 200

    def test_user_sees_only_their_own_notes(self):
        self.client.force_authenticate(self.user_1)
        response = self.client.get("/notes/")
        payload = response.json()
        assert len(payload) == 2
        for note in payload:
            assert note["author"] == url_for_user(self.user_1, True)
        assert response.status_code == 200

        self.client.force_authenticate(self.user_2)
        response = self.client.get("/notes/")
        payload = response.json()
        assert len(payload) == 2
        for note in payload:
            assert note["author"] == url_for_user(self.user_2, True)
        assert response.status_code == 200

    def test_user_can_not_access_other_users_notes(self):
        self.client.force_authenticate(self.user_1)
        response = self.client.get(url_for_note(self.note_2_1))
        assert response.status_code == 404
        response = self.client.get(url_for_note(self.note_2_2))
        assert response.status_code == 404

    def test_user_can_not_change_ownership(self):
        self.client.force_authenticate(self.user_1)
        note_url = url_for_note(self.note_1_1)
        payload = {"author": url_for_user(self.user_2, True)}
        # TODO: Should this throw an error instead of just getting ignored?
        response = self.client.patch(note_url, payload)
        note = response.json()
        assert note["author"] == url_for_user(self.user_1, True)

    def test_user_can_not_edit_other_users_notes(self):
        self.client.force_authenticate(self.user_1)
        note_url = url_for_note(self.note_2_1)
        payload = {"title": "updated", "tags": ["new"]}
        response = self.client.patch(note_url, payload)
        assert response.status_code == 404
        note = Note.objects.get(id=self.note_2_1.id)
        assert note.title != "updated"

    def test_user_can_not_delete_other_users_notes(self):
        self.client.force_authenticate(self.user_1)
        note_url = url_for_note(self.note_2_1)
        response = self.client.delete(note_url)
        assert response.status_code == 404
        note = Note.objects.get(id=self.note_2_1.id)
        assert note.id == self.note_2_1.id

    def test_user_can_search_notes_by_keyword(self):
        self.client.force_authenticate(self.user_1)
        # Should only match note_1_1
        response = self.client.get("/notes/?search=title1")
        payload = response.json()
        assert len(payload) == 1
        for note in payload:
            self.assertEquals(note["title"], self.note_1_1.title)
            self.assertEquals(note["body"], self.note_1_1.body)
            self.assertEquals(note["author"], url_for_user(self.user_1, True))
            self.assertEquals(note["tags"], [])
        assert response.status_code == 200

        # Should match note_1_1 and note_1_2
        response = self.client.get("/notes/?search=title")
        payload = response.json()
        assert len(payload) == 2
        assert response.status_code == 200

        # Should not match any notes
        response = self.client.get("/notes/?search=unknown")
        payload = response.json()
        assert len(payload) == 0
        assert response.status_code == 200
