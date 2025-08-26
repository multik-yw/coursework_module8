from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Habit
from .pagination import HabitPagination
from .serializers import HabitSerializer, HabitCreateSerializer, HabitUpdateSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter


class HabitListCreateView(generics.ListCreateAPIView):
    pagination_class = HabitPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["is_pleasant", "is_public"]
    ordering_fields = ["time", "created_at"]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return HabitCreateSerializer
        return HabitSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return HabitUpdateSerializer
        return HabitSerializer


class PublicHabitListView(generics.ListAPIView):
    serializer_class = HabitSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Habit.objects.filter(is_public=True)
    pagination_class = None  # Отключаем пагинацию для публичного списка


class MarkHabitCompletedView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    http_method_names = ["patch"]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.mark_completed()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
