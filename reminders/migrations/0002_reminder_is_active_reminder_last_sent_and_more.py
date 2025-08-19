from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reminders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reminder',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='reminder',
            name='last_sent',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reminder',
            name='next_run',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
