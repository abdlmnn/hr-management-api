from datetime import datetime
import os
from django.utils import timezone
from django.utils.html import escape
import secrets
import re


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


def format_plain_text_to_html(plain_text):
    """
    Converts plain text input from HR users to HTML format for email delivery.
    
    Rules:
    - Escapes HTML to prevent XSS attacks
    - Converts single newlines to <br> tags
    - Converts double newlines (paragraph breaks) to <br><br>
    - Preserves template variables (e.g., {applicant_full_name}, {job_name})
    - Trims trailing whitespace
    
    Args:
        plain_text (str): Plain text input from frontend
        
    Returns:
        str: HTML-formatted text ready for email delivery
        
    Example:
        Input: "Dear {applicant_full_name},\\n\\nCongratulations!"
        Output: "Dear {applicant_full_name},<br><br>Congratulations!"
    """
    if not plain_text:
        return ""
    
    # Escape HTML to prevent XSS (but preserve template variables)
    # Template variables are in format {variable_name}
    # We need to escape everything except the template variable placeholders
    
    # Split by template variables to preserve them
    # Pattern matches {variable_name} format
    template_pattern = r'(\{[a-zA-Z_][a-zA-Z0-9_]*\})'
    parts = re.split(template_pattern, plain_text)
    
    formatted_parts = []
    for part in parts:
        if re.match(template_pattern, part):
            # This is a template variable, keep it as-is
            formatted_parts.append(part)
        else:
            # This is regular text, escape HTML
            escaped = escape(part)
            formatted_parts.append(escaped)
    
    # Join back together
    escaped_text = ''.join(formatted_parts)
    
    # Convert newlines to <br> tags
    # Double newlines (paragraph breaks) become <br><br>
    # Single newlines become <br>
    # First, normalize multiple consecutive newlines to double newlines
    normalized = re.sub(r'\n{3,}', '\n\n', escaped_text)
    # Convert double newlines to <br><br>
    html_text = normalized.replace('\n\n', '<br><br>')
    # Convert remaining single newlines to <br>
    html_text = html_text.replace('\n', '<br>')
    
    # Trim trailing whitespace and <br> tags
    html_text = html_text.rstrip()
    
    return html_text
