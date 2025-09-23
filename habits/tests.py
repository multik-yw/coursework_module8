from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import User
from .models import Habit
from django.core.exceptions import ValidationError


class HabitModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="testpass123")

    def test_habit_creation(self):
        habit = Habit.objects.create(user=self.user, place="Дома", time="08:00:00", action="Пить воду", duration=30)
        self.assertEqual(str(habit), "Пить воду в 08:00:00")

    def test_mark_completed(self):
        habit = Habit.objects.create(user=self.user, place="Дома", time="08:00:00", action="Пить воду", duration=30)
        self.assertIsNone(habit.last_completed)
        habit.mark_completed()
        self.assertIsNotNone(habit.last_completed)


class HabitValidationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.pleasant_habit = Habit.objects.create(
            user=self.user, place="Дома", time="20:00:00", action="Чтение книги", duration=60, is_pleasant=True
        )

    def test_create_habit_with_both_reward_and_related_habit(self):
        habit = Habit(
            user=self.user,
            place="Парк",
            time="18:00:00",
            action="Гулять",
            duration=60,
            reward="Кофе",
            related_habit=self.pleasant_habit,
        )
        with self.assertRaises(ValidationError) as context:
            habit.full_clean()
        self.assertIn("Выберите что-то одно: вознаграждение или связанную привычку.", str(context.exception))

    def test_create_pleasant_habit_with_reward(self):
        habit = Habit(
            user=self.user,
            place="Дома",
            time="20:00:00",
            action="Смотреть сериал",
            duration=60,
            is_pleasant=True,
            reward="Попкорн",
        )
        with self.assertRaises(ValidationError) as context:
            habit.full_clean()
        self.assertIn("Приятная привычка не может иметь вознаграждение или быть связанной.", str(context.exception))

    def test_create_habit_with_invalid_duration(self):
        habit = Habit(user=self.user, place="Дома", time="08:00:00", action="Медитация", duration=121)
        with self.assertRaises(ValidationError) as context:
            habit.full_clean()
        self.assertIn("Время выполнения не должно превышать 120 секунд.", str(context.exception))

    def test_create_habit_with_invalid_frequency(self):
        habit = Habit(user=self.user, place="Дома", time="08:00:00", action="Зарядка", duration=30, frequency=0)
        with self.assertRaises(ValidationError) as context:
            habit.full_clean()
        self.assertIn("Периодичность должна быть от 1 до 7 дней.", str(context.exception))

    def test_create_habit_with_non_pleasant_related_habit(self):
        related_habit = Habit.objects.create(
            user=self.user, place="Дома", time="07:00:00", action="Чистить зубы", duration=120, is_pleasant=False
        )
        habit = Habit(
            user=self.user, place="Дома", time="08:00:00", action="Пить воду", duration=30, related_habit=related_habit
        )
        with self.assertRaises(ValidationError) as context:
            habit.full_clean()
        self.assertIn("Связанная привычка должна быть приятной.", str(context.exception))


class HabitAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.pleasant_habit = Habit.objects.create(
            user=self.user, place="Дома", time="20:00:00", action="Чтение книги", duration=60, is_pleasant=True
        )

        self.habit_data = {
            "place": "Дома",
            "time": "08:00:00",
            "action": "Пить воду",
            "duration": 30,
            "is_public": False,
            "frequency": 1,  # Добавьте обязательное поле
        }

    def test_create_habit(self):
        url = reverse("habit-list-create")
        response = self.client.post(url, self.habit_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 2)

    def test_create_habit_with_both_reward_and_related_habit_api(self):
        url = reverse("habit-list-create")
        data = {
            **self.habit_data,
            "reward": "Кофе",
            "related_habit": self.pleasant_habit.id,
            "frequency": 1,  # Добавляем обязательное поле
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Выберите что-то одно: вознаграждение или связанную привычку.", str(response.data))

    def test_create_pleasant_habit_with_reward_api(self):
        url = reverse("habit-list-create")
        data = {
            "place": "Дома",
            "time": "20:00:00",
            "action": "Смотреть сериал",
            "duration": 60,
            "is_pleasant": True,
            "reward": "Попкорн",
            "frequency": 1,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Приятная привычка не может иметь вознаграждение или быть связанной.",
            str(response.data),  # Просто проверяем всю строку ответа
        )

    def test_create_habit_with_invalid_duration_api(self):
        url = reverse("habit-list-create")
        data = {**self.habit_data, "duration": 121, "frequency": 1}  # Добавляем обязательное поле
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Время выполнения не должно превышать 120 секунд.", str(response.data))

    def test_create_habit_with_invalid_frequency_api(self):
        url = reverse("habit-list-create")
        data = {**self.habit_data, "frequency": 0}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Периодичность должна быть от 1 до 7 дней.", str(response.data))

    def test_mark_habit_completed(self):
        habit = Habit.objects.create(user=self.user, place="Дома", time="08:00:00", action="Пить воду", duration=30)
        url = reverse("habit-mark-completed", kwargs={"pk": habit.pk})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habit.refresh_from_db()
        self.assertIsNotNone(habit.last_completed)

    def test_public_habits_list(self):
        Habit.objects.create(
            user=self.user, place="Парк", time="18:00:00", action="Гулять", duration=60, is_public=True
        )
        url = reverse("public-habit-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
