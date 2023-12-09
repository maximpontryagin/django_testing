from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='Неавтор')
        cls.author = User.objects.create(username='Автор')
        cls.auth_reader = Client()
        cls.auth_author = Client()
        cls.auth_reader.force_login(cls.reader)
        cls.auth_author.force_login(cls.author)
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       slug='slug', author=cls.author)

    def test_note_in_object_list_authot(self):
        users_result = (
            (self.auth_author, True),
            (self.auth_reader, False),
        )
        for user, result in users_result:
            response = user.get(reverse('notes:list'))
            object_context = response.context['object_list']
            self.assertIs((self.note in object_context), result)

    def test_authorized_client_has_form(self):
        urls = (('notes:add', None), ('notes:edit', (self.note.slug,)),)
        for url, args in urls:
            self.client.force_login(self.author)
            response = self.client.get(reverse(url, args=args))
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm, msg=None)
