# Generated by Django 2.1.2 on 2019-03-28 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_auto_20190328_0934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apicase',
            name='update_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='创建时间'),
        ),
    ]
