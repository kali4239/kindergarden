# Generated by Django 5.1.5 on 2025-02-21 06:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kinder', '0023_alter_parent_parent_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.IntegerField()),
                ('score', models.FloatField()),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='kinder.student')),
            ],
        ),
    ]
