# Generated by Django 4.2.4 on 2023-09-15 22:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialm', '0002_profile_first_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='first_name',
        ),
    ]