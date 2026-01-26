from rest_framework import generics, permissions
from .serializers import (
    JobSerializer,
    PublicJobSerializer,
)
from .models import Job
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class JobView(generics.ListAPIView):
    queryset = Job.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'department', 'job_type']
    search_fields = ['name', 'job_description', 'requirements']
    ordering_fields = ['date_created', 'name', 'deadline']
    ordering = ['-id']


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


class PublicJobListView(generics.ListAPIView):
    """
    Public listing endpoint for applicant portal.
    Returns only active jobs and excludes jobs past deadline (if deadline is set).
    """

    permission_classes = (permissions.AllowAny,)
    serializer_class = PublicJobSerializer

    def get_queryset(self):
        today = timezone.localdate()
        return (
            Job.objects.filter(is_active=True)
            .filter(Q(deadline__isnull=True) | Q(deadline__gte=today))
            .order_by("-id")
        )
