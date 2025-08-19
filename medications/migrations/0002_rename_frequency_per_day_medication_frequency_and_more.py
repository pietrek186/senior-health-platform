from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('medications', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='medication',
            old_name='frequency_per_day',
            new_name='frequency',
        ),
        migrations.RemoveField(
            model_name='medication',
            name='dosage',
        ),
    ]
