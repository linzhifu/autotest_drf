# Generated by Django 2.1.2 on 2019-04-01 09:59

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('user', '0020_auto_20190331_1328'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.BooleanField(default=False, verbose_name='测试结果')),
                ('typedes', models.CharField(max_length=500, verbose_name='描述')),
                ('update_time', models.DateTimeField(auto_now_add=True, verbose_name='最后修改')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': '测试类型分类',
            },
        ),
        migrations.AddField(
            model_name='webmanager',
            name='result',
            field=models.BooleanField(default=False, verbose_name='测试结果'),
        ),
        migrations.AddField(
            model_name='webmanager',
            name='update_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='最后修改'),
            preserve_default=False,
        ),
    ]
