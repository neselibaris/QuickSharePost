# Generated by Django 4.2.4 on 2023-10-01 14:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialm', '0025_report_post'),
    ]

    operations = [
        migrations.RenameField(
            model_name='report',
            old_name='content',
            new_name='description',
        ),
    ]
