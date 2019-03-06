# Generated by Django 2.1.2 on 2019-03-05 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20190304_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='role',
            field=models.IntegerField(blank=True, choices=[(0, 'user'), (1, 'admin')], default=0, null=True),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='password',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='username',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]