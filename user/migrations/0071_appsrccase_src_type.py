# Generated by Django 2.1 on 2019-09-11 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0070_auto_20190905_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='appsrccase',
            name='src_type',
            field=models.CharField(default=1, max_length=100, verbose_name='脚本类型'),
            preserve_default=False,
        ),
    ]
