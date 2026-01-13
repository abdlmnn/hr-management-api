from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse, Http404
from .serializers import ApplicantSerializer
from .models import Applicant
import os


class ApplicantView(generics.ListAPIView):
    queryset = Applicant.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ApplicantSerializer


class AddApplicantView(generics.CreateAPIView):
    queryset = Applicant.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = ApplicantSerializer

    def perform_create(self, serializer):
        username = (
            self.request.user.username
            if self.request.user.is_authenticated
            else "anonymous"
        )

        serializer.save(updated_by=username)


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


class PendingApplicantView(generics.ListAPIView):
    queryset = Applicant.objects.filter(status="pending")
    # permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ApplicantSerializer
