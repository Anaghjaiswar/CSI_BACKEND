# Generated by Django 5.1.2 on 2025-02-26 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Task', '0003_alter_task_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending Task'), ('current', 'Current Task'), ('completed', 'Completed Task')], max_length=50),
        ),
    ]
