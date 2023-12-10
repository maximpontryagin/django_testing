from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='Неавтор')
        cls.auth_reader = Client()
        cls.auth_reader.force_login(cls.reader)
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'title': 'Заголовок form_data',
                         'text': 'Текст form_data', 'slug': 'slugform'}
        cls.note = Note.objects.create(title='Заголовок0', text='Текст',
                                       slug='slug10', author=cls.user)
        cls.add_url = reverse('notes:add')
        cls.succes_url = reverse('notes:success')
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_auth_user_can_create_note(self):
        note_count_after_fixtures = Note.objects.count()
        self.auth_client.post(self.add_url, data=self.form_data)
        self.assertEqual(Note.objects.count(),
                         note_count_after_fixtures + 1)
        note_last = Note.objects.last()
        self.assertEqual(note_last.title, self.form_data['title'])
        self.assertEqual(note_last.text, self.form_data['text'])
        self.assertEqual(note_last.slug, self.form_data['slug'])
        self.assertEqual(note_last.author, self.user)

    def test_anonymus_user_cant_create_note(self):
        note_count_after_fixtures = Note.objects.count()
        self.client.post(self.add_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), note_count_after_fixtures)

    def test_author_user_can_delete_note(self):
        note_count_after_fixtures = Note.objects.count()
        response = self.auth_client.post(self.delete_url)
        self.assertRedirects(response, self.succes_url)
        self.assertEqual(Note.objects.count(),
                         note_count_after_fixtures - 1)

    def test_auth_user_cant_delte_note(self):
        note_count_after_fixtures = Note.objects.count()
        response = self.auth_reader.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), note_count_after_fixtures)

    def test_user_cant_edit_note(self):
        note_bofore_change = self.note
        response = self.auth_reader.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note, note_bofore_change)

    def test_author_can_edit_note(self):
        response = self.auth_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.succes_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.user)

    def test_not_unique_slug(self):
        note_count_after_fixtures = Note.objects.count()
        form_data = self.form_data
        form_data['slug'] = self.note.slug
        response = self.auth_client.post(self.add_url, data=form_data)
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), note_count_after_fixtures)

    def test_empty_slug(self):
        note_count_after_fixtures = Note.objects.count()
        form_data = self.form_data
        form_data.pop('slug')
        response = self.auth_client.post(self.add_url, data=form_data)
        self.assertRedirects(response, self.succes_url)
        self.assertEqual(Note.objects.count(), note_count_after_fixtures + 1)
        new_note = Note.objects.last()
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
