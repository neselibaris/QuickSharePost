# Generated by Django 4.2.4 on 2023-10-01 13:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialm', '0021_profile_is_moderator'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'permissions': [('priv1_required', 'priv1 ile erişim izni')]},
        ),
        migrations.AlterModelOptions(
            name='likepost',
            options={'permissions': [('priv1_required', 'priv1 ile erişim izni')]},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'permissions': [('priv1_required', 'priv1 ile erişim izni')]},
        ),
        migrations.AlterModelOptions(
            name='profile',
            options={'permissions': [('priv1_required', 'priv1 ile erişim izni')]},
        ),
    ]
