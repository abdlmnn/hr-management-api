from rest_framework import generics, permissions
from .serializers import (
    JobTypeSerializer,
)
from .models import JobType


class JobTypeView(generics.ListAPIView):
    queryset = JobType.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobTypeSerializer


class AddJobTypeView(generics.CreateAPIView):
    queryset = JobType.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobTypeSerializer

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.username,
        )


class UpdateJobTypeView(generics.RetrieveUpdateAPIView):
    queryset = JobType.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobTypeSerializer
    lookup_field = "id"

    def perform_update(self, serializer):
        serializer.save(
            created_by=self.request.user.username,
        )


class DeleteJobTypeView(generics.DestroyAPIView):
    queryset = JobType.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobTypeSerializer
    lookup_field = "id"
