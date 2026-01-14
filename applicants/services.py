from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .models import Applicant
from .utils import generate_verification_token


verification_token_expiry = 1  # 1 min or 24 hours

@
def create_application(data, username):
    print("Debug data", data)

    applicant = Applicant.objects.filter(
        email__iexact=data.get("email"), job=data.get("job"), status="pending"
    ).first()

    token = generate_verification_token()

    if applicant:
        for attr, value in data.items():
            setattr(applicant, attr, value)

        applicant.verification_token = token
        applicant.token_created = timezone.now()
        applicant.updated_by = username
        applicant.save()
    else:
        applicant = Applicant.objects.create(
            **data,
            verification_token=token,
            token_created=timezone.now(),
            updated_by=username,
        )

    return applicant
