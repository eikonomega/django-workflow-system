# Generated by Django 3.1.8 on 2021-05-19 18:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_workflow_system', '0002_auto_20210518_1357'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='WorkflowStepDataGroup',
            new_name='WorkflowMetadata',
        ),
        migrations.AlterUniqueTogether(
            name='workflowmetadata',
            unique_together={('name', 'parent_group')},
        ),
    ]