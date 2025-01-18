# Generated by Django 5.1.4 on 2025-01-18 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_auto_20250118_0008'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='company_name',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='industry',
        ),
        migrations.AddField(
            model_name='regularcustomer',
            name='invoice',
            field=models.FileField(blank=True, null=True, upload_to='invoices/'),
        ),
        migrations.AddField(
            model_name='regularcustomer',
            name='other_documents',
            field=models.FileField(blank=True, null=True, upload_to='other_documents/'),
        ),
    ]
