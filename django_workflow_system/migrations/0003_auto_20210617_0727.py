# Generated by Django 3.1.8 on 2021-06-17 12:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_workflow_system', '0002_create_standard_user_input_types'),
    ]

    operations = [
        migrations.RenameField(
            model_name='workflowcollectionengagementdetail',
            old_name='user_response',
            new_name='user_responses',
        ),
    ]
