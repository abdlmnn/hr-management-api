from rest_framework import generics, permissions
from .serializers import (
    JobSerializer,
)
from .models import Job


class JobView(generics.ListAPIView):
    queryset = Job.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobSerializer


class AddJobView(generics.CreateAPIView):
    queryset = Job.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobSerializer

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.username,
        )


class UpdateJobView(generics.RetrieveUpdateAPIView):
    queryset = Job.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobSerializer
    lookup_field = "id"

    def perform_update(self, serializer):
        serializer.save(
            created_by=self.request.user.username,
        )


class DeleteJobView(generics.DestroyAPIView):
    queryset = Job.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobSerializer
    lookup_field = "id"
