# Generated by Django 4.2.1 on 2023-05-30 00:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gennifer', '0002_inferenceresult_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='algorithm',
            name='run_url',
        ),
        migrations.AddField(
            model_name='algorithm',
            name='url',
            field=models.CharField(default='localhost', max_length=128),
            preserve_default=False,
        ),
    ]
