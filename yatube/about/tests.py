from django.test import TestCase, Client


class StaticURLTests(TestCase):

    def setUp(self):
        self.quest_client = Client()

    def test_author(self):
        response = self.quest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_author_correct_template(self):
        response = self.quest_client.get('/about/author/')
        self.assertTemplateUsed(response, 'about/author.html')

    def test_tech(self):
        response = self.quest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_tech_correct_template(self):
        response = self.quest_client.get('/about/tech/')
        self.assertTemplateUsed(response, 'about/tech.html')
