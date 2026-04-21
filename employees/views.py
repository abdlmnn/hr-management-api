from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from applicants.models import Applicant
from employees.models import Employee
from employees.serializers import CreateEmployeeSerializer, EmployeeSerializer


class CreateEmployeeView(APIView):
    """
    Creates an employee by adding a hired applicant (internal HR flow; no verification email).
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = CreateEmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        username = (getattr(request.user, "username", None) or "sys")[:10]

        applicant = Applicant.objects.create(
            first_name=data["first_name"],
            middle_name=data.get("middle_name"),
            last_name=data["last_name"],
            email=data["email"].strip().lower(),
            contact_number=data["contact_number"],
            job=data["job"],
            status="hired",
            cover_letter="",
            updated_by=username,
            verification_token=None,
            token_created=None,
        )

        employee = Employee.objects.select_related(
            "applicant",
            "job",
            "job__department",
            "job__job_type",
            "employment_type",
        ).get(applicant=applicant)

        update_fields = []
        if data["employment_type"] != employee.employment_type:
            employee.employment_type = data["employment_type"]
            update_fields.append("employment_type")
        if data["date_started"] != employee.date_started:
            employee.date_started = data["date_started"]
            update_fields.append("date_started")
        if update_fields:
            employee.updated_by = username
            update_fields.append("updated_by")
            employee.save(update_fields=update_fields)
            employee.refresh_from_db()

        out = EmployeeSerializer(employee, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)


class EmployeeView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_active", "employment_type", "job"]
    search_fields = [
        "employee_id",
        "applicant__full_name",
        "applicant__first_name",
        "applicant__middle_name",
        "applicant__last_name",
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
