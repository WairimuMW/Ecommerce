# Generated by Django 3.1.7 on 2021-08-08 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arts', '0015_auto_20210806_1815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artistprofile',
            name='artprof',
            field=models.ImageField(blank=True, default='profpic.png', null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='customerprofile',
            name='custprof',
            field=models.ImageField(blank=True, default='profpic.png', null=True, upload_to=''),
        ),
    ]