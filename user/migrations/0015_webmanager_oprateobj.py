# Generated by Django 2.1.2 on 2019-03-28 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_auto_20190328_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='webmanager',
            name='oprateOBj',
            field=models.CharField(max_length=200, null=True, verbose_name='操作类型'),
        ),
    ]