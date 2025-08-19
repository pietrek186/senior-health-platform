from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medications', '0002_rename_frequency_per_day_medication_frequency_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='medication',
            name='dosage',
            field=models.CharField(blank=True, max_length=100, verbose_name='Dawkowanie (np. 1 tabletka 2× dziennie)'),
        ),
        migrations.AddField(
            model_name='medication',
            name='dosage_ml_per_time',
            field=models.FloatField(blank=True, null=True, verbose_name='Dawka syropu (ml)'),
        ),
        migrations.AddField(
            model_name='medication',
            name='form',
            field=models.CharField(choices=[('tablet', 'Tabletki'), ('syrup', 'Syrop')], default='tablet', max_length=10, verbose_name='Postać leku'),
        ),
        migrations.AddField(
            model_name='medication',
            name='volume_ml',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Objętość syropu (ml)'),
        ),
    ]
