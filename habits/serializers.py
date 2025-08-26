from rest_framework import serializers
from .models import Habit
from .validators import validate_habit
from django.utils import timezone
from datetime import timedelta


class HabitSerializer(serializers.ModelSerializer):
    is_overdue = serializers.SerializerMethodField()

    duration = serializers.IntegerField(
        min_value=1,
        max_value=120,
        error_messages={
            "min_value": "Время выполнения должно быть не менее 1 секунды.",
            "max_value": "Время выполнения не должно превышать 120 секунд.",
        },
    )

    class Meta:
        model = Habit
        fields = [
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "frequency",
            "reward",
            "duration",
            "is_public",
            "created_at",
            "last_completed",
            "is_overdue",
        ]
        read_only_fields = ("user", "created_at", "last_completed", "is_overdue")

    def get_is_overdue(self, obj):
        if not obj.last_completed:
            return True
        next_completion = obj.last_completed + timedelta(days=obj.frequency)
        return timezone.now() > next_completion

    def validate(self, data):
        validate_habit(data)
        return data

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class HabitCreateSerializer(serializers.ModelSerializer):
    frequency = serializers.IntegerField(
        min_value=1,
        max_value=7,
        error_messages={
            "min_value": "Периодичность должна быть от 1 до 7 дней.",
            "max_value": "Периодичность должна быть от 1 до 7 дней.",
        },
    )

    duration = serializers.IntegerField(
        min_value=1,
        max_value=120,
        error_messages={
            "min_value": "Время выполнения должно быть не менее 1 секунды.",
            "max_value": "Время выполнения не должно превышать 120 секунд.",
        },
    )

    class Meta:
        model = Habit
        fields = [
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "frequency",
            "reward",
            "duration",
            "is_public",
        ]

    def validate(self, data):
        validate_habit(data)

        if data.get("is_pleasant") and (data.get("reward") or data.get("related_habit")):
            raise serializers.ValidationError("Приятная привычка не может иметь вознаграждение или быть связанной.")
        return data


class HabitUpdateSerializer(serializers.ModelSerializer):
    frequency = serializers.IntegerField(
        min_value=1,
        max_value=7,
        error_messages={
            "min_value": "Периодичность должна быть от 1 до 7 дней.",
            "max_value": "Периодичность должна быть от 1 до 7 дней.",
        },
        required=False,
    )

    duration = serializers.IntegerField(
        min_value=1,
        max_value=120,
        error_messages={
            "min_value": "Время выполнения должно быть не менее 1 секунды.",
            "max_value": "Время выполнения не должно превышать 120 секунд.",
        },
        required=False,
    )

    class Meta:
        model = Habit
        fields = [
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "frequency",
            "reward",
            "duration",
            "is_public",
        ]
