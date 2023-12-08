from django.test import TestCase
from django.urls import reverse
from notes.models import Note
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Неавтор')
        cls.note = Note.objects.create(title='Заголовок0', text='Текст',
                                       slug='slug', author=cls.author)

    def test_note_in_object_list_authot(self):
        users_result = (
            (self.author, True),
            (self.reader, False),
        )
        for user, result in users_result:
            self.client.force_login(user)
            response = self.client.get(reverse('notes:list'))
            object_list = response.context['object_list']
            self.assertIs((self.note in object_list), result)

    def test_note_in_notes(self):
        all_notes = []
        for index in range(1, 5):
            notes = Note(title='Заголовок', text='Текст',
                         slug=f'slug{index}', author=self.author)
            all_notes.append(notes)
        Note.objects.bulk_create(all_notes)
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        self.assertEqual(object_list[1].slug, 'slug1')

    def test_authorized_client_has_form(self):
        urls = (('notes:add', None), ('notes:edit', (self.note.slug,)),)
        for url, args in urls:
            self.client.force_login(self.author)
            response = self.client.get(reverse(url, args=args))
            self.assertIn('form', response.context)
