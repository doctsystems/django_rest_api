from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@email.com', password='pass123'):
    # crea usuario de ejemplo
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):

    def test_create_user_with_email_successful(self):
        # Probar crear nuevo usuario con email
        email = 'test@email.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        # test email para nuevo usuario normalizado
        email = 'test@EMAIL.COM'
        user = get_user_model().objects.create_user(email, 'Testpass123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        # Nuevo usuario con email invalido
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'Testpass123')

    def test_create_new_super_user(self):
        # probar super usuario creado
        email = 'superuser@email.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_superuser(email=email, password=password)

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_user(self):
        # probar representacion en cadena de texto del tag
        tag = models.Tag.objects.create(user=sample_user(), name='Meat')

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        # probar representacion en cadena de texto del ingrediente 
        ingredient = models.Ingredient.objects.create(user=sample_user(), name='Banana')

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        # probar representacion en cadena de texto de las recetas 
        recipe = models.Recipe.objects.create(user=sample_user(), title='Titulo de receta', time_minutes=5, price=5.00)

        self.assertEqual(str(recipe), ingredient.title)