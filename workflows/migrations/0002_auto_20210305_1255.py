# Generated by Django 3.1.3 on 2021-03-05 12:55

from django.db import migrations, models
import workflows.models.collection


class Migration(migrations.Migration):

    dependencies = [
        ('workflows', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflowcollection',
            name='code',
            field=models.CharField(max_length=200, validators=[workflows.models.collection.validate_code]),
        ),
    ]
