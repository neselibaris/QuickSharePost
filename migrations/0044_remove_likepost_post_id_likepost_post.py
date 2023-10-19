# Generated by Django 4.2.6 on 2023-10-18 14:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('socialm', '0043_likepost_created_on'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='likepost',
            name='post_id',
        ),
        migrations.AddField(
            model_name='likepost',
            name='post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='socialm.post'),
        ),
    ]