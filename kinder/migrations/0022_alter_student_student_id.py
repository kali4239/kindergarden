# Generated by Django 5.1.5 on 2025-02-20 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kinder', '0021_alter_parent_parent_id_alter_student_student_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='student_id',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
