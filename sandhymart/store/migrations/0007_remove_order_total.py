# Generated by Django 3.1.5 on 2021-02-04 12:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_auto_20210203_2212'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='total',
        ),
    ]
