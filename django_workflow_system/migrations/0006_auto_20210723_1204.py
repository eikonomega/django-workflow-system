# Generated by Django 3.1.8 on 2021-07-23 17:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_workflow_system', '0005_auto_20210720_0834'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='workflowcollectiondependency',
            table='workflow_system_collection_dependency',
        ),
        migrations.AlterModelTable(
            name='workflowcollectionrecommendation',
            table='workflow_system_collection_recommendation',
        ),
    ]
