# Generated by Django 5.1.3 on 2024-11-09 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voter_analytics', '0002_voter_delete_result'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voter',
            name='apt_num',
            field=models.TextField(blank=True, null=True),
        ),
    ]
