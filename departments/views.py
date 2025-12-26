from rest_framework import generics, permissions
from .serializers import (
    DepartmentSerializer,
)
from .models import Department


class DepartmentView(generics.ListAPIView):
    queryset = Department.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DepartmentSerializer


class AddDepartmentView(generics.CreateAPIView):
    queryset = Department.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DepartmentSerializer

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.username,
        )


class UpdateDepartmentView(generics.RetrieveUpdateAPIView):
    queryset = Department.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DepartmentSerializer
    lookup_field = "id"

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username,
        )


class DeleteDepartmentView(generics.DestroyAPIView):
    queryset = Department.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DepartmentSerializer
    lookup_field = "id"
