# Generated by Django 2.2.4 on 2019-09-01 21:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_billingprofile_customer_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billingprofile',
            name='customer_id',
        ),
    ]
