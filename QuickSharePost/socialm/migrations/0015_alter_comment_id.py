# Generated by Django 4.2.4 on 2023-09-29 21:59

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('socialm', '0014_rename_comment_comment_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False),
        ),
    ]