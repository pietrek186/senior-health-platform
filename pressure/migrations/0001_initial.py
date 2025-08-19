import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PressureMeasurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('systolic', models.IntegerField(verbose_name='Ciśnienie skurczowe (mmHg)')),
                ('diastolic', models.IntegerField(verbose_name='Ciśnienie rozkurczowe (mmHg)')),
                ('date', models.DateField(verbose_name='Data pomiaru')),
                ('time', models.TimeField(verbose_name='Godzina pomiaru')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
