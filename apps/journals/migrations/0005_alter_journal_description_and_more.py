# Generated by Django 5.1.4 on 2024-12-21 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journals', '0004_journalissue_downloads_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journal',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='journal',
            name='description_en',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='journal',
            name='description_ru',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='journal',
            name='description_uz',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
    ]
