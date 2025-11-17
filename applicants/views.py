from rest_framework import generics, permissions
from .serializers import (
    ApplicantSerializer,
)
from .models import Applicant


class ApplicantView(generics.ListAPIView):
    queryset = Applicant.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ApplicantSerializer


class AddApplicantView(generics.CreateAPIView):
    queryset = Applicant.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = ApplicantSerializer

    def perform_create(self, serializer):
        serializer.save(
            updated_by=self.request.user.username,
        )


class UpdateApplicantView(generics.RetrieveUpdateAPIView):
    queryset = Applicant.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ApplicantSerializer
    lookup_field = "id"

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username,
        )


class DeleteApplicantView(generics.DestroyAPIView):
    queryset = Applicant.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ApplicantSerializer
    lookup_field = "id"
