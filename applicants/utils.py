from datetime import datetime
import os
from django.utils import timezone
import secrets


def generate_verification_token():
    return secrets.token_urlsafe(32)


def now():
    return timezone.now()
    # return datetime.now()


def valid_id_upload_path(instance, filename):
    """
    Store valid_id as: applicants/<applicant_name>/<applicant_name>_valid_id.pdf
    """
    safe_name = (
        instance.full_name.replace(" ", "_") if instance.full_name else "unknown"
    )
    return f"applicants/{safe_name}/{safe_name}_valid_id.pdf"


def resume_upload_path(instance, filename):
    """
    Store resume as: applicants/<applicant_name>/<applicant_name>_resume.pdf
    """
    safe_name = (
        instance.full_name.replace(" ", "_") if instance.full_name else "unknown"
    )
    return f"applicants/{safe_name}/{safe_name}_resume.pdf"


def format_report_as_html(report_data, period_name):
    """
    Formats the report data into an HTML table.
    """
    if not report_data:
        return "<p>No applicant data found for the selected period.</p>"

    total_applicants = sum(report_data.values())

    html = f"""
    <h3>Applicant Status Report ({period_name})</h3>
    <p>Total new applicants: {total_applicants}</p>
    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 50%;">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th>Status</th>
                <th>Count</th>
            </tr>
        </thead>
        <tbody>
    """
    for status, count in report_data.items():
        html += f"<tr><td>{status.title()}</td><td>{count}</td></tr>"

    html += """
        </tbody>
    </table>
    """
    return html
