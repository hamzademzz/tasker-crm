# Generated by Django 5.1.4 on 2025-01-18 00:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_alter_regularcustomer_service_dates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regularcustomer',
            name='service_dates',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
