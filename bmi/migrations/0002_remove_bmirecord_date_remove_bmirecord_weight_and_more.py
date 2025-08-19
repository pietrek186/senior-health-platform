import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bmi', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bmirecord',
            name='date',
        ),
        migrations.RemoveField(
            model_name='bmirecord',
            name='weight',
        ),
        migrations.AddField(
            model_name='bmirecord',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2025, 8, 1, 13, 13, 25, 718225, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
    ]
