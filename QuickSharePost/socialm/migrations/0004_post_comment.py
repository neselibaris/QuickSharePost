# Generated by Django 4.2.4 on 2023-09-20 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialm', '0003_remove_profile_first_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
    ]
