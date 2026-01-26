## Goal

## Flow guide for deployment configs

Expose a safe, stable backend API for an applicant-facing website **without login**, using **email verification** to confirm submissions, while keeping HR/admin APIs protected by JWT.

This plan addresses the current gaps:
- No public jobs listing
- Applicant can potentially set `status` on create
- “Resend verification” path does not reliably update token/timestamps
- Verification link UX is API JSON (not user-friendly redirect)
- CORS is wide open; no throttling/anti-spam
- Input validation is permissive for a public form

---

## Target API contract (high-level)

### Public (applicant site)
- **List open jobs**: `GET /api/v1/public/jobs/`
  - Only `is_active=true`
  - Exclude past-deadline jobs (if `deadline` is set)
  - Include fields needed by the applicant site (name, dept, type, description, requirements, skills, deadline)
- **Submit application**: `POST /api/v1/public/applicants/`
  - Accept: `full_name`, `email`, `contact_number`, `job`, optional `cover_letter`, optional `resume` PDF, optional `valid_id` PDF
  - Always creates/keeps applicant as `pending` until verified
- **Verify application**: `GET /api/v1/public/applicants/verify/<token>/`
  - If valid & not expired → mark as `applied`, clear token, trigger emails
  - If invalid/expired → redirect to frontend “expired” page

### Authenticated (HR/admin site)
Keep existing endpoints under `api/v1/...` with `IsAuthenticated` (JWT), including:
- Manage jobs, applicants, departments, templates, notifications, reports

---

## Implementation plan (step-by-step)

### 1) Add a public jobs listing endpoint
- **Add new endpoint** under a `public` namespace to avoid loosening permissions on existing HR endpoints.
  - Example route: `GET /api/v1/public/jobs/`
- **Filtering rules**:
  - `is_active=true`
  - If `deadline` is present, include only where `deadline >= today`
- **Output**:
  - Reuse existing `JobSerializer` or create a “public” serializer that excludes internal fields (e.g., `created_by`, `updated_by`) if not needed.

Acceptance criteria:
- Applicant site can render job cards and a job details page without JWT.

---

### 2) Lock down applicant-controlled fields (critical security fix)
Problem: current public create flow likely allows passing `status` in request body.

Actions:
- **Make `status` server-controlled** for public create:
  - Ensure serializer used by public create does **not accept** `status` (or sets it read-only).
- Ensure public create does not accept `updated_by`, `verification_token`, `token_created`, `date_applied`.
- On verify endpoint, status transitions should be controlled and explicit:
  - `pending` → `applied` only

Acceptance criteria:
- Submitting `status=hired` (or any status) in public create has no effect.

---

### 3) Fix resend/duplicate “pending” logic in `create_application`
Problem: when a `pending` applicant exists, code generates a token but doesn’t persist it, yet still sends email.

Actions:
- If a pending applicant exists:
  - Enforce “recently sent” rule (already present) to reduce spam
  - Otherwise **rotate token** and **update `token_created`**
  - Optionally update uploaded files/cover letter if you allow resubmission before verification (decide behavior)
- Add tests for:
  - First submission creates pending + token + email queued
  - Second submission within lock window errors
  - Second submission after lock window rotates token and sends a fresh link

Acceptance criteria:
- Resent verification email always contains a valid, unexpired token linked to the applicant row.

---

### 4) Improve verification UX: redirect to applicant website
Current verify endpoint returns JSON. For a link clicked from email, redirect is usually better.

Actions:
- Add frontend URLs (env-configured):
  - `APPLICANT_PORTAL_VERIFY_SUCCESS_URL`
  - `APPLICANT_PORTAL_VERIFY_EXPIRED_URL`
  - `APPLICANT_PORTAL_VERIFY_INVALID_URL`
- Change verify endpoint behavior:
  - On success: redirect to success page
  - On invalid token: redirect to invalid page
  - On expired token: redirect to expired page (with CTA “resubmit”)

Acceptance criteria:
- Clicking email verification link results in a friendly page on the applicant site.

---

### 5) Add anti-spam and abuse protection for public endpoints
Public endpoints must be protected from automated spam and email bombing.

Actions (minimum viable):
- **DRF throttling** for:
  - application submission
  - verification endpoint
- **CAPTCHA** (optional but recommended):
  - Verify captcha token server-side before accepting submission
- Add a lightweight **email domain/format validation** and normalize `email__iexact` usage (already used in queries).

Acceptance criteria:
- Burst submissions are rate-limited.
- Verification endpoint cannot be hammered without throttling.

---

### 6) Tighten CORS and production settings
Current `CORS_ORIGIN_ALLOW_ALL=True` is fine for dev but risky for prod.

Actions:
- In production:
  - Set `CORS_ORIGIN_ALLOW_ALL=False`
  - Set `CORS_ALLOWED_ORIGINS=[<applicant_portal_domain>, <hr_admin_domain>]`
- Replace `ALLOWED_HOSTS=["*"]` in prod with explicit hosts.
- Ensure `DEBUG=False` in prod and secrets come from environment.

Acceptance criteria:
- Only your known frontend origins can call the API from browsers.

---

### 7) Strengthen applicant input validation
Actions:
- Use proper email validation (e.g., `EmailField` / serializer validation).
- Normalize `full_name` trimming; basic phone validation (format/length).
- Validate file uploads:
  - already restricted to PDF by extension; also enforce size limits at API level

Acceptance criteria:
- Obvious invalid emails/phones are rejected with clear validation errors.

---

### 8) Observability and operational safeguards
Actions:
- Log key events:
  - application created (pending)
  - verification email queued/sent
  - application verified (applied)
  - throttling triggers (rate limit hit)
- Ensure Celery/Redis are configured reliably in prod.
- Confirm cleanup task for pending apps aligns with token expiry (both 24h).

Acceptance criteria:
- You can troubleshoot “I didn’t get the email” and “link expired” cases quickly.

---

## Environment variables (add/update)

- **API_BASE_URL**: base URL used in verification email links (currently used)
- **APPLICANT_PORTAL_VERIFY_SUCCESS_URL**: where to redirect after successful verify
- **APPLICANT_PORTAL_VERIFY_EXPIRED_URL**: where to redirect for expired token
- **APPLICANT_PORTAL_VERIFY_INVALID_URL**: where to redirect for invalid/used token
- **CORS_ALLOWED_ORIGINS** (or explicit config in settings per environment)
- Email:
  - `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
- Celery/Redis:
  - `CELERY_BROKER_URL` (or `BROKER_URL`), `REDIS_URL`

---

## Rollout checklist

- **API endpoints ready**:
  - Public jobs list works without JWT
  - Public applicant submit + verify work end-to-end
- **Security**:
  - Applicant cannot set `status` or internal fields
  - Throttling enabled for public routes
  - CORS restricted for prod
- **Email**:
  - Verification emails sent and links are correct
  - Verify redirects to applicant site pages
- **Background jobs**:
  - Celery worker running
  - Beat scheduler running (cleanup + daily report)
- **Docs for coworker**:
  - Provide endpoint list, required fields, and example error responses

---

## Suggested commit message (use when implementation is complete)

docs(deployment): plan public applicant API + verification hardening

