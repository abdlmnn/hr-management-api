from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from users.serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import ChangePasswordSerializer
from django.contrib.auth import update_session_auth_hash


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.data["old_password"]):
                return Response(
                    {"message": "Wrong old password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Set the new password
            user.set_password(serializer.data["new_password"])
            user.save()

            # Update the session hash to prevent logout after password change
            update_session_auth_hash(request, user)

            return Response(
                {"message": "Password changed successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
