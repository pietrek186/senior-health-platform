from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medications', '0003_medication_dosage_medication_dosage_ml_per_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medication',
            name='dosage_ml_per_time',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Dawka syropu (ml)'),
        ),
        migrations.AlterField(
            model_name='medication',
            name='quantity',
            field=models.PositiveIntegerField(verbose_name='Ilość tabletek (lub objętość syropu w ml)'),
        ),
    ]
