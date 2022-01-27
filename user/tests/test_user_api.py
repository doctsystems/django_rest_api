from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    # testear API publica del usuario

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        # probar creear usuario con un payload exitoso
        payload = {'email': 'test@email.com', 'password': 'pass123', 'name': 'test name'}

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        # probar crear un usuario que ya existe
        payload = {'email': 'test@email.com', 'password': 'pass123', 'name': 'test name'}
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        # probar que la contraseña es corta o menor a 5 caracteres
        payload = {'email': 'test@email.com', 'password': 'pass', 'name': 'test name'}

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exist = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exist)

    def test_create_token_for_user(self):
        # probar que se crea token para usuario
        payload = {'email': 'test@email.com', 'password': 'pass123', 'name': 'test name'}
        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        # probar que el token no es creado con credenciales invalidas
        create_user(email='test@email.com', password='Testpass')
        payload = {'email': 'test@email.com', 'password': 'wrong'}

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        # prueba que no se crea un token si no existe el usuario
        payload = {'email': 'test@email.com', 'password': 'pass123', 'name': 'test name'}

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        # probar que el email y contraseña sean requeridas
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        # prueba que la autenticacion sea requerida
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    # testear el API Privado del usuario

    def setUp(self):
        self.user = create_user(email='test@email.com', password='pass123', name='name user')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        # probar obtener perdil para usuario con login
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'name': self.user.name, 'email': self.user.email})

    def test_post_me_not_allowed(self):
        # prueba que el post no sea permitido
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        # probar que el usuario esta siendo actualizado si esta autenticado
        payload = {'name': 'new name', 'password': 'newpass'}

        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
