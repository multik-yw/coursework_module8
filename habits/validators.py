from rest_framework.exceptions import ValidationError



def validate_habit(data):
    if data.get("reward") and data.get("related_habit"):
        raise ValidationError(
            "Выберите что-то одно: вознаграждение или связанную привычку."
        )

    if data.get("is_pleasant") and (data.get("reward") or data.get("related_habit")):
        raise ValidationError(
            "Приятная привычка не может иметь вознаграждение или быть связанной."
        )

    if data.get("duration", 0) > 120:
        raise ValidationError("Время выполнения не должно превышать 120 секунд.")

    if data.get("frequency", 1) < 1 or data.get("frequency", 1) > 7:
        raise ValidationError("Периодичность должна быть от 1 до 7 дней.")