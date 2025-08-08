from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User


class UserTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="adminpass"
        )
        self.user = User.objects.create_user(
            email="user@example.com", password="userpass"
        )
        self.user_data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "telegram_id": "123456",
        }

    def test_jwt_auth(self):
        url = reverse("token_obtain_pair")
        data = {"email": "user@example.com", "password": "userpass"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_jwt_auth_invalid_credentials(self):
        url = reverse("token_obtain_pair")
        data = {"email": "user@example.com", "password": "wrongpass"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_registration(self):
        url = reverse("register")
        response = self.client.post(url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_registration_missing_email(self):
        url = reverse("register")
        data = {"password": "testpass"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_list_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_list_non_admin(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_retrieve_self(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("user-detail", args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_user_retrieve_other_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("user-detail", args=[self.admin.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.admin.email)

    def test_user_update_self(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("user-detail", args=[self.user.id])
        data = {"telegram_id": 654321}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.telegram_id, 654321)

    def test_user_update_password(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("user-detail", args=[self.user.id])
        data = {"password": "newpassword123"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))

    def test_user_update_other_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("user-detail", args=[self.admin.id])
        data = {"telegram_id": "should_not_work"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"], "Вы можете редактировать только свой аккаунт"
        )

    def test_user_delete_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("user-detail", args=[self.user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 1)

    def test_user_delete_self(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("user-detail", args=[self.user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.filter(id=self.user.id).count(), 0)

    def test_user_delete_other_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("user-detail", args=[self.admin.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"], "Вы можете удалить только свой аккаунт"
        )

    def test_email_uniqueness(self):
        url = reverse("register")
        data = {"email": "user@example.com", "password": "testpass"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_telegram_id_max_length(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("user-detail", args=[self.user.id])
        data = {"telegram_id": "a" * 51}  # 51 символ при максимуме 50
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("telegram_id", response.data)