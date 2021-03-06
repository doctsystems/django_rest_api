from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    # probar los API tags disponibles publicamente

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        # prueba que login sea requerido para obtener los tags
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    # probar los API tags privados

    def setUp(self):
        self.user = get_user_model().objects.create_user('test@email.com', 'pass123')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        # probar obtener los tags
        Tag.objects.create(user=self.user, name='Meat')
        Tag.objects.create(user=self.user, name='Banana')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        # probar obtener tags del usuario actual
        user2 = get_user_model().objects.create_user('otro@email.com', 'pass123')
        Tag.objects.create(user=user2, name='Apple')
        tag = Tag.objects.create(user=self.user, name='Confort food')

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        # probar crear nuevo tag
        payload = {'name': 'Simple'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(user=self.user, name=payload['name']).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        # prueba crear nuevo tag invalido
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipe(self):
        # probar filtro de tags basados en recetas
        tag1 = Tag.objects.create(user=self.user, name='Meat')
        tag2 = Tag.objects.create(user=self.user, name='Banana')
        recipe = Recipe.objects.create(title='Test recipe', time_minutes=13, price=12.50, user=self.user)
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        # probar filtro de tags asignados por items unicos
        tag = Tag.objects.create(user=self.user, name='Meat')
        recipe1 = Recipe.objects.create(title='Test bresk', time_minutes=15, price=12.50, user=self.user)
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(title='Test fast', time_minutes=30, price=20.50, user=self.user)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
