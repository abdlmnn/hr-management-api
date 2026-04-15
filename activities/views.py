from django.db.models import QuerySet
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from rest_framework import generics, permissions

from .models import Activity
from .serializers import ActivitySerializer


class ActivityView(generics.ListAPIView):
    serializer_class = ActivitySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> QuerySet[Activity]:
        qs = Activity.objects.all().order_by("-id")

        # Optional filters for calendar month/range queries:
        # - `start` and `end` should be ISO 8601 datetimes.
        start_raw = self.request.query_params.get("start")
        end_raw = self.request.query_params.get("end")

        if start_raw:
            start_dt = parse_datetime(start_raw)
            if start_dt:
                if timezone.is_naive(start_dt):
                    start_dt = timezone.make_aware(
                        start_dt,
                        timezone.get_default_timezone(),
                    )
                qs = qs.filter(when__gte=start_dt)

        if end_raw:
            end_dt = parse_datetime(end_raw)
            if end_dt:
                if timezone.is_naive(end_dt):
                    end_dt = timezone.make_aware(
                        end_dt,
                        timezone.get_default_timezone(),
                    )
                qs = qs.filter(when__lte=end_dt)

        return qs


class AddActivityView(generics.CreateAPIView):
    queryset = Activity.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ActivitySerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.username)


class RetrieveActivityView(generics.RetrieveAPIView):
    queryset = Activity.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ActivitySerializer
    lookup_field = "id"


class UpdateActivityView(generics.RetrieveUpdateAPIView):
    queryset = Activity.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ActivitySerializer
    lookup_field = "id"

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class DeleteActivityView(generics.DestroyAPIView):
    queryset = Activity.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ActivitySerializer
    lookup_field = "id"

