from rest_framework import generics, permissions
from .serializers import (
    JobSerializer,
)
from .models import Job
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class JobView(generics.ListAPIView):
    queryset = Job.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'department', 'job_type']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']


class AddJobView(generics.CreateAPIView):
    queryset = Job.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobSerializer

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.username,
        )


class RetrieveJobView(generics.RetrieveAPIView):
    queryset = Job.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobSerializer
    lookup_field = "id"


class UpdateJobView(generics.RetrieveUpdateAPIView):
    queryset = Job.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobSerializer
    lookup_field = "id"

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username,
        )


class DeleteJobView(generics.DestroyAPIView):
    queryset = Job.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobSerializer
    lookup_field = "id"
