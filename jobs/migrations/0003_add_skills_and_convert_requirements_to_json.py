from django.db import migrations, models
import json


def convert_requirements_to_json(apps, schema_editor):
    # text to array
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT id, requirements FROM jobs WHERE requirements IS NOT NULL AND requirements != ''")
        for job_id, text in cursor.fetchall():
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            json_data = json.dumps(lines) if lines else json.dumps([text])
            cursor.execute("UPDATE jobs SET requirements = %s WHERE id = %s", [json_data, job_id])


def reverse_requirements_to_text(apps, schema_editor):
    # array to text
    Job = apps.get_model('jobs', 'Job')
    for job in Job.objects.all():
        if job.requirements:
            try:
                data = json.loads(job.requirements) if isinstance(job.requirements, str) else job.requirements
                job.requirements = '\n'.join(str(item) for item in data) if isinstance(data, list) else str(data)
                job.save(update_fields=['requirements'])
            except (json.JSONDecodeError, TypeError):
                pass


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_job_updated_by'),
    ]

    operations = [
        migrations.RunPython(convert_requirements_to_json, reverse_requirements_to_text),
        migrations.AddField(
            model_name='job',
            name='skills',
            field=models.JSONField(blank=True, default=list, help_text='List of skills required for this job (array of strings)'),
        ),
        migrations.AlterField(
            model_name='job',
            name='requirements',
            field=models.JSONField(blank=True, default=list, help_text='List of job requirements (array of strings)'),
        ),
    ]

