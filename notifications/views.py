from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Count, Q
from .serializers import (
    EmailNotificationSerializer,
)
from .models import EmailNotification
from django.utils import timezone
from django.core.mail import EmailMessage, get_connection
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import os
from src.utils import email_notification_body


class NotificationLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 12
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 10000  # Increased to allow fetching all notifications for dashboard stats


class ListEmailNotificationsView(generics.ListAPIView):
    queryset = EmailNotification.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmailNotificationSerializer
    pagination_class = NotificationLimitOffsetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_sent']
    search_fields = ['recipient', 'subject']
    ordering_fields = ['date_created', 'last_attempt']
    ordering = ['-date_created']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Handle date range filtering
        date_from = self.request.query_params.get('date_created__gte', None)
        date_to = self.request.query_params.get('date_created__lte', None)
        
        if date_from:
            queryset = queryset.filter(date_created__gte=date_from)
        if date_to:
            queryset = queryset.filter(date_created__lte=date_to)
        
        return queryset


class AddEmailNotificationView(generics.CreateAPIView):
    queryset = EmailNotification.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmailNotificationSerializer

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.username,
        )


class EmailNotificationSummaryView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        summary = EmailNotification.objects.aggregate(
            sent=Count("id", filter=Q(is_sent=True)),
            failed=Count("id", filter=Q(is_sent=False) & ~Q(error_message__isnull=True) & ~Q(error_message="")),
            pending=Count("id", filter=Q(is_sent=False) & (Q(error_message__isnull=True) | Q(error_message=""))),
        )

        return Response(summary, status=status.HTTP_200_OK)
        
class EmailNotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmailNotification.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmailNotificationSerializer
    lookup_field = 'id'
    
    def perform_update(self, serializer):
        serializer.save(
            created_by=self.request.user.username,
        )
        
class UpdateEmailNotificationView(generics.UpdateAPIView):
    queryset = EmailNotification.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmailNotificationSerializer
    lookup_field = 'id'
    
    def perform_update(self, serializer):
        serializer.save(
            created_by=self.request.user.username,
        )
        
class DeleteEmailNotificationView(generics.DestroyAPIView):
    queryset = EmailNotification.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmailNotificationSerializer
    lookup_field = 'id'


class ResendEmailNotificationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, id):
        try:
            notification = EmailNotification.objects.get(id=id)
        except EmailNotification.DoesNotExist:
            return Response(
                {"success": False, "message": "Email notification not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Reset notification for resend
        notification.is_sent = False
        notification.error_message = None
        notification.retry_count += 1
        notification.last_attempt = timezone.now()
        notification.save()

        # Attempt to send immediately
        try:
            html_content = email_notification_body(email_body=notification.body)
            msg = EmailMessage(
                subject=notification.subject,
                body=html_content,
                from_email=os.getenv("EMAIL_HOST_USER"),
                to=[notification.recipient],
            )
            msg.content_subtype = "html"

            with get_connection() as connection:
                connection.send_messages([msg])

            # Mark as sent
            notification.is_sent = True
            notification.error_message = None
            notification.save()

            return Response(
                {
                    "success": True,
                    "message": "Email notification resent successfully.",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            # Store error message
            notification.is_sent = False
            notification.error_message = str(e)
            notification.save()

            return Response(
                {
                    "success": False,
                    "message": f"Failed to resend email: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class BulkResendEmailNotificationsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        ids = request.data.get('ids', [])
        if not ids or not isinstance(ids, list):
            return Response(
                {"success": False, "message": "Invalid request. 'ids' must be a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        notifications = EmailNotification.objects.filter(id__in=ids)
        if not notifications.exists():
            return Response(
                {"success": False, "message": "No email notifications found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        results = {
            "success": 0,
            "failed": 0,
            "errors": [],
        }

        for notification in notifications:
            # Reset notification for resend
            notification.is_sent = False
            notification.error_message = None
            notification.retry_count += 1
            notification.last_attempt = timezone.now()
            notification.save()

            # Attempt to send immediately
            try:
                html_content = email_notification_body(email_body=notification.body)
                msg = EmailMessage(
                    subject=notification.subject,
                    body=html_content,
                    from_email=os.getenv("EMAIL_HOST_USER"),
                    to=[notification.recipient],
                )
                msg.content_subtype = "html"

                with get_connection() as connection:
                    connection.send_messages([msg])

                # Mark as sent
                notification.is_sent = True
                notification.error_message = None
                notification.save()
                results["success"] += 1

            except Exception as e:
                # Store error message
                notification.is_sent = False
                notification.error_message = str(e)
                notification.save()
                results["failed"] += 1
                results["errors"].append({
                    "id": notification.id,
                    "recipient": notification.recipient,
                    "error": str(e),
                })

        return Response(
            {
                "success": results["success"] > 0,
                "message": f"Bulk resend completed: {results['success']} sent, {results['failed']} failed.",
                "results": results,
            },
            status=status.HTTP_200_OK,
        )

        
