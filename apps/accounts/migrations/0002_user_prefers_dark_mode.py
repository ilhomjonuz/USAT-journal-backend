# Generated by Django 5.1.4 on 2024-12-24 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='prefers_dark_mode',
            field=models.BooleanField(default=False),
        ),
    ]
