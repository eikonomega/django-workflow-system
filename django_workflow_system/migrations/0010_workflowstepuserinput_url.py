# Generated by Django 3.1.12 on 2021-11-11 17:45

from django.db import migrations, models
import django_workflow_system.utils.media_files


class Migration(migrations.Migration):

    dependencies = [
        ('django_workflow_system', '0009_update_user_input_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflowstepuserinput',
            name='url',
            field=models.ImageField(max_length=200, null=True, upload_to=django_workflow_system.utils.media_files.workflow_step_media_location),
        ),
    ]
