# Generated by Django 5.1.2 on 2024-10-17 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='image_url',
        ),
        migrations.AddField(
            model_name='article',
            name='image_fil',
            field=models.ImageField(blank=True, upload_to=''),
        ),
    ]
