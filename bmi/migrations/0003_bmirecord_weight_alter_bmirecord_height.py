from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bmi', '0002_remove_bmirecord_date_remove_bmirecord_weight_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bmirecord',
            name='weight',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='bmirecord',
            name='height',
            field=models.FloatField(null=True),
        ),
    ]
