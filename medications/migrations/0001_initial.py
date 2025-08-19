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
            name='Medication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nazwa leku')),
                ('quantity', models.PositiveIntegerField(verbose_name='Ilość tabletek w opakowaniu')),
                ('dosage', models.CharField(max_length=100, verbose_name='Dawkowanie (np. 1 tabletka 2x dziennie)')),
                ('start_date', models.DateField(verbose_name='Data rozpoczęcia stosowania')),
                ('frequency_per_day', models.PositiveIntegerField(default=1, verbose_name='Częstotliwość dawkowania (ile razy dziennie)')),
                ('prescription_required', models.BooleanField(default=False, verbose_name='Czy lek na receptę?')),
                ('expiration_date', models.DateField(blank=True, null=True, verbose_name='Data ważności')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
