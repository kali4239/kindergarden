# Generated by Django 5.1.6 on 2025-03-13 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kinder', '0046_remove_xogame_board_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='xogame',
            name='board_state',
            field=models.JSONField(default=list),
        ),
    ]
