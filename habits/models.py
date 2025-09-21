from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from django.core.exceptions import ValidationError
from config.celery import app as celery_app


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    place = models.CharField(max_length=100, verbose_name="Место")
    time = models.TimeField(verbose_name="Время")
    action = models.CharField(max_length=200, verbose_name="Действие")
    is_pleasant = models.BooleanField(default=False, verbose_name="Приятная привычка")
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
    )
    frequency = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        verbose_name="Периодичность (дни)",
    )
    reward = models.CharField(max_length=200, blank=True, verbose_name="Вознаграждение")
    duration = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)], verbose_name="Время на выполнение (сек)"
    )
    is_public = models.BooleanField(default=False, verbose_name="Публичная")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    last_completed = models.DateTimeField(null=True, blank=True, verbose_name="Последнее выполнение")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(check=models.Q(duration__lte=120), name="duration_max_120_seconds"),
            models.CheckConstraint(
                check=models.Q(frequency__gte=1) & models.Q(frequency__lte=7), name="frequency_between_1_and_7"
            ),
        ]


def __str__(self):
    return f"{self.action} в {self.time}"


def clean(self):
    if self.duration > 120:
        raise ValidationError("Время выполнения не должно превышать 120 секунд.")
    if self.frequency < 1 or self.frequency > 7:
        raise ValidationError("Периодичность должна быть от 1 до 7 дней.")

    if self.reward and self.related_habit:
        raise ValidationError("Выберите из предложенного: вознаграждение или связанную привычку.")

    if self.is_pleasant and (self.reward or self.related_habit):
        raise ValidationError("Приятная привычка не может иметь вознаграждение или быть связанной.")

    if self.related_habit and not self.related_habit.is_pleasant:
        raise ValidationError("Связанная привычка должна быть приятной.")

    if self.related_habit and self.related_habit.id == self.id:
        raise ValidationError("Привычка не может ссылаться на саму себя.")


def save(self, *args, **kwargs):
    self.full_clean()
    super().save(*args, **kwargs)


def mark_completed(self):
    """Отметка выполненной привычки и отправка уведомления"""
    self.last_completed = timezone.now()
    self.save()

    if self.user.telegram_id:
        message = f"Привычка выполнена: {self.action} в {self.time}"
        celery_app.send_task("habits.tasks.send_telegram_notification", args=[self.user.telegram_id, message])


def needs_reminder(self):
    """Проверка отправки напоминания"""
    if not self.last_completed:
        return True
    next_reminder = self.last_completed + timedelta(days=self.frequency)
    return timezone.now() > next_reminder
