# Generated by Django 3.1.3 on 2021-03-05 12:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflows', '0002_auto_20210303_1815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflowcollectionassignment',
            name='expiration',
            field=models.DateField(default=datetime.date(2021, 4, 5)),
        ),
    ]
