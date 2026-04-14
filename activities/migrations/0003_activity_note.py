from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("activities", "0002_activity_when_end"),
    ]

    operations = [
        migrations.AddField(
            model_name="activity",
            name="note",
            field=models.TextField(
                blank=True,
                help_text="Optional notes or extra context for this activity.",
                null=True,
            ),
        ),
    ]
