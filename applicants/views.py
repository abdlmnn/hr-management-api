from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from django.http import FileResponse, Http404
from .serializers import ApplicantSerializer
from .models import Applicant
from .services import (
    create_application,
    send_applicant_status_notification,
    generate_applicant_status_report,
)
from datetime import timedelta
from django.utils import timezone
import os
from .tasks import verification_token_expiry


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


class VerifyApplicantView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, token):
        try:
            applicant = Applicant.objects.get(
                verification_token=token, status="pending"
            )
        except Applicant.DoesNotExist:
            raise Http404("This verification link is invalid or has already been used.")

        if applicant.token_created:
            expiry_time = applicant.token_created + timedelta(
                minutes=verification_token_expiry
            )
            if timezone.now() > expiry_time:
                return Response(
                    {
                        "message": "This verification link has expired. Please submit a new application to receive a new link."
                    }
                )

        applicant.status = "applied"
        applicant.verification_token = None
        applicant.save(update_fields=["status", "verification_token"])

        return Response(
            {
                "message": "Your application has been successfully verified and submitted."
            }
        )


class SendApplicantEmailView(APIView):
    # permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, id):
        """
        Manually triggers a status-based email notification for a given applicant.
        """
        try:
            if send_applicant_status_notification(applicant_id=id):
                return Response(
                    {
                        "message": "Sending email has been successfully queued for sending."
                    }
                )
            else:
                return Response(
                    {
                        "message": "No email was sent for the applicant's current status."
                    },
                    status=400,
                )
        except NotFound as e:
            return Response({"error": str(e)}, status=404)
        except Exception as e:
            return Response(
                {
                    "error": "An unexpected error occurred while trying to send the email."
                },
                status=500,
            )


class DailyReportView(APIView):
    # permission_classes = permissions.IsAuthenticated

    def get(self, request):
        """
        Returns applicant status report data as JSON for frontend dashboards.
        """
        report_data, period_name = generate_applicant_status_report()

        if report_data is None:
            return Response({"error": "Failed to generate report data."}, status=500)

        return Response({"period_name": period_name, "report_data": report_data})
