from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    # probar API Ingredientes de acceso publicos
    
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        # probar que login es necesario para acceder al endpoint
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientsApiTests(TestCase):
    # probar API privada de ingradientes

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('test@mail.com', 'testpass')
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        # probar obtener lista de ingredientes
        Ingredient.objects.create(user=self.user, name='milk')
        Ingredient.objects.create(user=self.user, name='cheese')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        # probar obtener ingredientes solo del usuario autenticado
        user2 = get_user_model().objects.create_user('user2@mail.com', 'pass123')
        Ingredient.objects.create(user=user2, name='vinagre')
        ingredient = Ingredient.objects.create(user=self.user, name='tutuma')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        # probar crear nuevo ingrediente
        payload = {'name': 'fresh'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(user=self.user, name=payload['name']).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        # prueba crear nuevo ingrediente invalido
        payload = {'name':''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)