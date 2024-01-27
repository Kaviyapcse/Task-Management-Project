# Generated by Django 4.0.6 on 2024-01-26 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_remove_task_due_data_task_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('to-do', 'TO-DO'), ('in-progress', 'IN-PROGRESS'), ('done', 'DONE')], default='to-do', max_length=20),
        ),
    ]
