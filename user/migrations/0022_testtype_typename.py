# Generated by Django 2.1.2 on 2019-04-01 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0021_auto_20190401_0959'),
    ]

    operations = [
        migrations.AddField(
            model_name='testtype',
            name='typename',
            field=models.CharField(default=1, max_length=500, verbose_name='名称'),
            preserve_default=False,
        ),
    ]
