from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.filters import OrderingFilter, SearchFilter

from employees.models import Employee
from employees.serializers import EmployeeSerializer


class EmployeeView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_active", "employment_type", "job"]
    search_fields = [
        "employee_id",
        "applicant__full_name",
        "applicant__email",
        "applicant__contact_number",
        "job__name",
        "employment_type__name",
    ]
    ordering_fields = ["id", "date_started", "date_created", "employee_id"]
    ordering = ["-id"]

    def get_queryset(self):
        queryset = Employee.objects.select_related(
            "applicant",
            "job",
            "job__department",
            "job__job_type",
            "employment_type",
        ).filter(applicant__status="hired")

        department_id = self.request.query_params.get("department")
        if department_id:
            queryset = queryset.filter(job__department_id=department_id)

        return queryset


class RetrieveEmployeeView(generics.RetrieveAPIView):
    queryset = Employee.objects.select_related(
        "applicant",
        "job",
        "job__department",
        "job__job_type",
        "employment_type",
    )
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmployeeSerializer
    lookup_field = "id"


class UpdateEmployeeView(generics.RetrieveUpdateAPIView):
    queryset = Employee.objects.select_related(
        "applicant",
        "job",
        "job__department",
        "job__job_type",
        "employment_type",
    )
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmployeeSerializer
    lookup_field = "id"

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)
