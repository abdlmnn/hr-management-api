from rest_framework import generics, permissions
from .serializers import (
    EmailNotificationSerializer,
)
from .models import EmailNotification
from rest_framework import permissions


class ListEmailNotificationsView(generics.ListAPIView):
    queryset = EmailNotification.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmailNotificationSerializer


class AddEmailNotificationView(generics.CreateAPIView):
    queryset = EmailNotification.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmailNotificationSerializer

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.username,
        )
