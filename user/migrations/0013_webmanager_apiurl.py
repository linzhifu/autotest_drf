# Generated by Django 2.1.2 on 2019-03-28 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_auto_20190328_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='webmanager',
            name='apiurl',
            field=models.CharField(max_length=200, null=True, verbose_name='url地址'),
        ),
    ]
