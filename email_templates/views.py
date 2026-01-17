from rest_framework import generics, permissions
from .models import EmailTemplate
from .serializers import EmailTemplateSerializer


class EmailTemplateView(generics.ListAPIView):
    queryset = EmailTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmailTemplateSerializer


class AddEmailTemplateView(generics.CreateAPIView):
    queryset = EmailTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmailTemplateSerializer


class RetrieveEmailTemplateView(generics.RetrieveAPIView):
    queryset = EmailTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmailTemplateSerializer
    lookup_field = "id"


class UpdateEmailTemplateView(generics.RetrieveUpdateAPIView):
    queryset = EmailTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmailTemplateSerializer
    lookup_field = "id"


class DeleteEmailTemplateView(generics.DestroyAPIView):
    queryset = EmailTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmailTemplateSerializer
    lookup_field = "id"