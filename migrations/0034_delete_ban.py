# Generated by Django 4.2.4 on 2023-10-03 18:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialm', '0033_alter_ban_created_at_alter_ban_description_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Ban',
        ),
    ]