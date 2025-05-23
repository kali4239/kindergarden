# Generated by Django 5.1.6 on 2025-03-06 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kinder', '0042_delete_chimpgamerecord_delete_puzzlegamerecord_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PuzzleGameRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_name', models.CharField(max_length=255, unique=True)),
                ('topic', models.CharField(max_length=50)),
                ('level', models.IntegerField()),
                ('time_taken', models.FloatField()),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PuzzleImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=50)),
                ('image', models.ImageField(upload_to='puzzle_images/')),
            ],
        ),
    ]
