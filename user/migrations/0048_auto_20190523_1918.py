# Generated by Django 2.1.2 on 2019-05-23 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0047_auto_20190523_1116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='adminPsw',
            field=models.CharField(default='Lin5535960', max_length=20, verbose_name='管理员密码'),
        ),
        migrations.AlterField(
            model_name='project',
            name='adminUser',
            field=models.CharField(default='linzhifu221@163.com', max_length=20, verbose_name='管理员账户'),
        ),
        migrations.AlterField(
            model_name='project',
            name='testPsw',
            field=models.CharField(default='123', max_length=20, verbose_name='测试密码'),
        ),
        migrations.AlterField(
            model_name='project',
            name='testUser',
            field=models.CharField(default='17388730192@163.com', max_length=20, verbose_name='测试账户'),
        ),
    ]