from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from users.models import User
from rest_framework.viewsets import GenericViewSet


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "list":
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=["get"])
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get", "patch", "delete"])
    def retrieve(self, request, pk=None):
        user = self.get_object()
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method == "PATCH":
            return self.update(request, pk)
        elif request.method == "DELETE":
            return self.destroy(request, pk)

    @action(detail=False, methods=["patch"])
    def set_telegram_id(self, request):
        user = request.user
        telegram_id = request.data.get("telegram_id")

        if not telegram_id:
            return Response({"error": "telegram_id обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        user.telegram_id = telegram_id
        user.save()
        return Response({"status": "Telegram ID успешно обновлен"}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_staff and instance != request.user:
            return Response(
                {"detail": "Вы можете редактировать только свой аккаунт"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if "password" in request.data:
            instance.set_password(request.data["password"])
            instance.save()
            return Response(status=status.HTTP_200_OK)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_staff or instance == request.user:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Вы можете удалить только свой аккаунт"},
            status=status.HTTP_403_FORBIDDEN,
        )
