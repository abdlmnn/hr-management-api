## Applicant Portal Backend Notes (for me + for wiring the registration page)

I’m wiring the applicant registration page to the backend. This is my quick checklist + manual.

---

## Public endpoints (no login)

- **1) List open jobs**: `GET /api/v1/public/jobs/`
  - Returns only jobs where `is_active=true` and not past `deadline` (if deadline exists).
  - I use `id` from this response as the value for the application’s `job` field.

- **2) Submit an application**: `POST /api/v1/applicants/add/`
  - Creates a `pending` application and sends a verification email.
  - Required fields: `full_name`, `email`, `contact_number`, `job`
  - Optional fields: `cover_letter`, `resume` (pdf), `valid_id` (pdf), `captcha_token`

- **3) Verify application** (email link): `GET /api/v1/applicants/<token>/verify/`
  - Valid token → sets status to `applied`, clears token, then redirects (if configured).

---

## Environment variables (copy/paste list)

### Core (runtime)
- `DEBUG` (`True` in dev, `False` in prod)
- `SECRET_KEY`

### API base URL (used to build the verification link in email)
- `API_BASE_URL`

### Applicant portal verification redirects (recommended)
- `APPLICANT_PORTAL_VERIFY_SUCCESS_URL`
- `APPLICANT_PORTAL_VERIFY_EXPIRED_URL`
- `APPLICANT_PORTAL_VERIFY_INVALID_URL`

### Production host + CORS (required when `DEBUG=False`)
- `ALLOWED_HOSTS` (comma-separated)
- `CORS_ALLOWED_ORIGINS` (comma-separated)

### Throttling (optional tuning)
- `PUBLIC_APPLICANT_SUBMIT_RATE` (default `10/hour`)
- `PUBLIC_APPLICANT_VERIFY_RATE` (default `60/hour`)

### Upload size limit (optional tuning)
- `APPLICANT_UPLOAD_MAX_MB` (default `5`)

### CAPTCHA (optional but recommended)
- `CAPTCHA_SECRET_KEY` (enables server-side verification)
- `CAPTCHA_VERIFY_URL` (optional; defaults to reCAPTCHA verify URL)
  - reCAPTCHA: `https://www.google.com/recaptcha/api/siteverify`
  - hCaptcha: `https://hcaptcha.com/siteverify`

### Email (required for verification emails)
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`

### Redis/Celery (required for background email sending + locks)
- `CELERY_BROKER_URL` (or `BROKER_URL`)
- `REDIS_URL`

---

## Manual (what each feature does)

### Applicant submission is “pending until verified”
- **What**: When I submit `POST /api/v1/applicants/add/`, the backend creates the applicant with `status=pending`.
- **Why**: The application is only considered real once the email is verified.
- **How it behaves**:
  - It sends a verification email containing a token link.
  - Clicking the token link sets `status=applied`.

### Applicants cannot set their own status
- **What**: Even if the frontend sends `status=hired`, the backend ignores it.
- **Why**: Prevents privilege escalation from public clients.
- **How it’s enforced**: The public create serializer treats `status` as read-only.

### Token resend behavior (pending re-submit)
- **What**: If the same person submits again for the same job while still `pending`, backend may resend verification.
- **Why**: Supports “I didn’t get the email / link expired” without creating garbage rows.
- **How it behaves**:
  - If a token email was sent in the last **15 minutes**, backend blocks resend.
  - After cooldown, backend rotates `verification_token` + `token_created` and re-sends.

### Verification link redirect (better UX)
- **What**: `GET /api/v1/applicants/<token>/verify/` redirects the browser to the applicant portal.
- **Why**: The user should land on the frontend, not a raw API JSON response.
- **How**:
  - success → `APPLICANT_PORTAL_VERIFY_SUCCESS_URL`
  - expired → `APPLICANT_PORTAL_VERIFY_EXPIRED_URL`
  - invalid/used → `APPLICANT_PORTAL_VERIFY_INVALID_URL`
  - If these are not set, API falls back to JSON/404.

### IP throttling (rate limiting)
- **What**: Public endpoints are limited per IP.
- **Why**: Reduces spam and protects email infrastructure.
- **Where it applies**:
  - `POST /api/v1/applicants/add/`
  - `GET /api/v1/applicants/<token>/verify/`

### CAPTCHA (server-side verification)
- **What**: The backend verifies `captcha_token` with the provider using `CAPTCHA_SECRET_KEY`.
- **Why**: Frontend CAPTCHA alone is not enough (attackers can call the API directly).
- **How**:
  - If `CAPTCHA_SECRET_KEY` is set → backend requires `captcha_token` on submit.
  - If not set → CAPTCHA is not enforced.

### Input validation (public create)
- **Email** must be a valid email format.
- **Full name** is trimmed and must be at least 2 characters.
- **Contact number** must be 7–30 chars, only digits/spaces/`+`/`-`/parentheses, and contain at least 7 digits.
- **Uploads** are pdf-only (model validator) + size limited (see below).

---

## How to adjust (where I change important configs)

### Change upload size limit
- **How**: set env `APPLICANT_UPLOAD_MAX_MB`
- **Where enforced**: `hr-management-api/applicants/serializers.py` (`ApplicantCreateSerializer._max_upload_bytes`)

### Change throttling rates
- **How**: set env:
  - `PUBLIC_APPLICANT_SUBMIT_RATE`
  - `PUBLIC_APPLICANT_VERIFY_RATE`
- **Where enforced**:
  - Views: `hr-management-api/applicants/views.py`
  - Throttle logic: `hr-management-api/applicants/throttles.py`
  - Default rate values: `hr-management-api/src/settings.py` (`REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]`)

### Change verification redirect pages
- **How**: set env:
  - `APPLICANT_PORTAL_VERIFY_SUCCESS_URL`
  - `APPLICANT_PORTAL_VERIFY_EXPIRED_URL`
  - `APPLICANT_PORTAL_VERIFY_INVALID_URL`
- **Where enforced**: `hr-management-api/applicants/views.py` (`VerifyApplicantView`)

### Enable/disable CAPTCHA enforcement
- **How**:
  - Enable: set `CAPTCHA_SECRET_KEY`
  - Set provider endpoint (optional): `CAPTCHA_VERIFY_URL`
- **Where enforced**:
  - Verification function: `hr-management-api/src/captcha.py`
  - Called from: `hr-management-api/applicants/views.py` (`AddApplicantView.perform_create`)

### Lock down prod CORS + allowed hosts
- **How** (prod): set env `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`
- **Where enforced**: `hr-management-api/src/settings.py`

