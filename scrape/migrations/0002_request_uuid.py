# Generated by Django 2.2 on 2020-06-11 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrape', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='uuid',
            field=models.UUIDField(null=True),
        ),
    ]