from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.http import FileResponse, Http404
from .serializers import ApplicantSerializer
from .models import Applicant
from .services import create_application, verification_token_expiry
from datetime import timedelta
from django.utils import timezone
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import redirect
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

        try:
            applicant = create_application(
                data=serializer.validated_data,
                username=username,
            )
        except ValidationError as e:
            raise e

        # Attach the instance to serializer so DRF returns it
        serializer.instance = applicant


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


class VerifyApplicantView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, token):
        try:
            applicant = Applicant.objects.get(
                verification_token=token, status="pending"
            )
        except Applicant.DoesNotExist:
            raise Http404("Applicant not found or already verified")

        if applicant.token_created:
            # for testing 1 min, default 24 hrs
            expiry = applicant.token_created + timedelta(
                minutes=verification_token_expiry
            )

            if timezone.now() > expiry:
                return Response(
                    {"message": "Verification link has expired, Please apply again"}
                )

        applicant.status = "applied"
        applicant.verification_token = None
        applicant.save()

        # redirect("https://localhost:3000/") for frontend
        return Response(
            {"message": "Applicant verified successfully, Application submitted"}
        )
