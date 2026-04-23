# Public API Endpoints (Production Reference)

This document describes the public-facing endpoints exposed by the HR Management API.

- Base path: `/api/v1`
- Content type: `application/json` unless endpoint accepts multipart upload
- Authentication: endpoints in this document are intentionally public (`AllowAny`)
- Error envelope: standardized by `custom_exception_handler`

## Public Endpoints Summary

1. `GET /api/v1/public/jobs/`
2. `POST /api/v1/applicants/add/`
3. `GET /api/v1/applicants/{token}/verify/`

---

## 1) List Public Jobs

`GET /api/v1/public/jobs/`

### Purpose

Returns jobs intended for applicant portal consumption.

### Access

- Public (`AllowAny`)

### Behavior

- Returns only jobs where:
  - `is_active = true`
  - `deadline` is null OR `deadline >= today` (Asia/Manila local date)
- Ordered by newest first (`-id`)

### Success Response (`200`)

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 123,
      "name": "Backend Developer",
      "department": 2,
      "department_name": "IT",
      "job_type": 1,
      "job_type_name": "Full-time",
      "job_description": "Build and maintain backend services.",
      "requirements": ["Python", "Django"],
      "skills": ["REST API", "SQL"],
      "deadline": "2026-05-30",
      "is_active": true
    }
  ]
}
```

---

## 2) Submit Applicant (Public Application)

`POST /api/v1/applicants/add/`

### Purpose

Creates a new applicant record (or refreshes pending application details) and queues verification email.

### Access

- Public (`AllowAny`)

### Request Content Types

- `application/json` (no file upload)
- `multipart/form-data` (with `valid_id`/`resume`)

### Request Fields

Required:

- `first_name` (string, non-empty, max 100)
- `last_name` (string, non-empty, max 100)
- `email` (valid email format)
- `contact_number` (Philippine mobile format: `09XXXXXXXXX`, `639XXXXXXXXX`, or `+639XXXXXXXXX`)
- `job` (job id)

Optional:

- `middle_name` (string, max 100)
- `cover_letter` (string)
- `valid_id` (file, PDF only)
- `resume` (file, PDF only)
- `captcha_token` (required when CAPTCHA secret is configured)

### File Upload Rules (Server-Enforced)

- `valid_id`: PDF only (`.pdf`, and when content type is present it must be `application/pdf`)
- `resume`: PDF only (`.pdf`, and when content type is present it must be `application/pdf`)
- Max size per file: `APPLICANT_UPLOAD_MAX_MB` (default: `25 MB`)

### Business Rules

- `status` and `date_applied` are server-controlled; client input is ignored/rejected as serializer rules apply.
- `full_name` is derived from name parts and is not writable.
- If same email+job has non-pending application within 24 hours, request is rejected.
- If same email+job has `pending` application:
  - if within resend cooldown (~15 minutes), rejected
  - otherwise pending record is refreshed and verification token rotates

### Example (Multipart)

```bash
curl -X POST "https://<host>/api/v1/applicants/add/" \
  -F "first_name=Juan" \
  -F "middle_name=Santos" \
  -F "last_name=Dela Cruz" \
  -F "email=juan@example.com" \
  -F "contact_number=09123456789" \
  -F "job=12" \
  -F "cover_letter=I am interested in this position." \
  -F "valid_id=@/path/to/valid-id.pdf;type=application/pdf" \
  -F "resume=@/path/to/resume.pdf;type=application/pdf" \
  -F "captcha_token=<token>"
```

### Success Response (`201`)

Returns applicant payload (serializer response).

### Validation Error Response (`400`)

```json
{
  "success": false,
  "errors": {
    "resume": ["Only PDF files are allowed."]
  },
  "message": "Validation failed"
}
```

Possible field messages include:

- `valid_id`: `"Only PDF files are allowed."`, `"File is too large. Maximum size is <n> MB."`
- `resume`: `"Only PDF files are allowed."`, `"File is too large. Maximum size is <n> MB."`
- `captcha_token`: `"CAPTCHA is required."`, `"Invalid CAPTCHA. Please try again."`, `"CAPTCHA verification failed. Please try again."`
- `contact_number`: format validation error

---

## 3) Verify Applicant Token

`GET /api/v1/applicants/{token}/verify/`

### Purpose

Verifies applicant email token, transitions status from `pending` to `applied`, and redirects user to configured portal URL.

### Access

- Public (`AllowAny`)
- Throttled by scope: `public_applicant_verify` (default rate: `60/hour`)

### Redirect Behavior

Configured by environment variables:

- `APPLICANT_PORTAL_VERIFY_SUCCESS_URL`
- `APPLICANT_PORTAL_VERIFY_EXPIRED_URL`
- `APPLICANT_PORTAL_VERIFY_INVALID_URL`

Flow:

- Invalid token / no pending applicant -> redirect to invalid URL (if configured)
- Expired token (>24h from token creation) -> redirect to expired URL (if configured)
- Valid token -> applicant status set to `applied`, token cleared, redirect to success URL (if configured)

### Notes

- This endpoint is redirect-oriented for browser flows, not a JSON API contract.
- If redirect env vars are missing, response behavior may vary by deployment and should be treated as misconfiguration for production.

---

## Standard Error Envelope

Most DRF errors are transformed into:

```json
{
  "success": false,
  "errors": {
    "<field>": ["<message>"]
  },
  "message": "Validation failed"
}
```

Where `message` prefers `errors.detail[0]` when present; otherwise generic fallback.

---

## Production Security Notes

1. Keep public surface minimal: only endpoints listed above should remain `AllowAny`.
2. Enable and tune throttling:
   - `PUBLIC_APPLICANT_SUBMIT_RATE` (currently defined, but submit throttle class in view is commented out)
   - `PUBLIC_APPLICANT_VERIFY_RATE`
3. Enforce CAPTCHA in production:
   - set `CAPTCHA_SECRET_KEY`
   - optionally set `CAPTCHA_VERIFY_URL` for provider
4. Enforce strict CORS and hosts:
   - `ALLOWED_HOSTS`
   - `CORS_ALLOWED_ORIGINS`
5. Keep file limits conservative via `APPLICANT_UPLOAD_MAX_MB`.

---

## Change Management

When adding a new public endpoint:

1. Require product/security review.
2. Add throttling scope and rate.
3. Add explicit input validation and tests.
4. Update this document in the same pull request.

---

## Code Mapping (Route -> Source of Truth)

Use this section when changing behavior so updates are applied in the correct files.

### `GET /api/v1/public/jobs/`

- Route registration:
  - `src/urls.py` (includes `src.public_urls`)
  - `src/public_urls.py` (`path("jobs/", PublicJobListView.as_view(), ...)`)
- View logic:
  - `jobs/views.py` -> `PublicJobListView`
- Response schema:
  - `jobs/serializers.py` -> `PublicJobSerializer`
- Data model:
  - `jobs/models.py` -> `Job`

### `POST /api/v1/applicants/add/`

- Route registration:
  - `src/urls.py` (includes `applicants.urls`)
  - `applicants/urls.py` (`path("add/", AddApplicantView.as_view(), ...)`)
- View logic:
  - `applicants/views.py` -> `AddApplicantView`
- Request/response validation:
  - `applicants/serializers.py` -> `ApplicantCreateSerializer`
  - `applicants/serializers.py` -> `ApplicantUploadValidationMixin` (PDF/type/size checks)
  - `applicants/serializers.py` -> `ApplicantNameWriteMixin` (name/contact rules)
- Core business flow:
  - `applicants/services.py` -> `create_application` (dedupe, cooldown, token rotation, email queue)
- CAPTCHA enforcement:
  - `src/captcha.py` -> `verify_captcha`
- File model constraints:
  - `applicants/models.py` -> `Applicant.valid_id` / `Applicant.resume`
- Tests to update:
  - `applicants/tests.py` -> `PublicApplicantCreateTests`

### `GET /api/v1/applicants/{token}/verify/`

- Route registration:
  - `applicants/urls.py` (`path("<str:token>/verify/", VerifyApplicantView.as_view(), ...)`)
- View logic:
  - `applicants/views.py` -> `VerifyApplicantView`
- Token/status model:
  - `applicants/models.py` -> `Applicant.verification_token`, `Applicant.token_created`, `Applicant.status`
- Redirect target configuration:
  - `APPLICANT_PORTAL_VERIFY_SUCCESS_URL`
  - `APPLICANT_PORTAL_VERIFY_EXPIRED_URL`
  - `APPLICANT_PORTAL_VERIFY_INVALID_URL`
- Tests to update:
  - `applicants/tests.py` -> `ApplicantVerifyRedirectTests`

### Cross-Cutting Public API Infrastructure

- Error response envelope:
  - `src/utils.py` -> `custom_exception_handler`
- Global DRF and throttling config:
  - `src/settings.py` -> `REST_FRAMEWORK`
  - Keys: `PUBLIC_APPLICANT_SUBMIT_RATE`, `PUBLIC_APPLICANT_VERIFY_RATE`
- Public endpoint inventory entrypoint:
  - `src/urls.py`
