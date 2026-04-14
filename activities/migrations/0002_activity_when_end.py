from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("activities", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="activity",
            name="when_end",
            field=models.DateTimeField(
                blank=True,
                help_text="Optional end time for multi-day activities.",
                null=True,
            ),
        ),
    ]
