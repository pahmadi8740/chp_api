# Generated by Django 3.2.6 on 2021-08-10 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('date_time', models.DateTimeField(auto_now=True)),
                ('query', models.JSONField(default=dict)),
                ('status', models.CharField(default='', max_length=100)),
                ('chp_version', models.CharField(default='', max_length=100)),
                ('chp_data_version', models.CharField(default='', max_length=100)),
                ('pybkb_version', models.CharField(default='', max_length=100)),
                ('chp_client_version', models.CharField(default='', max_length=100)),
                ('chp_utils_version', models.CharField(default='', max_length=100)),
            ],
        ),
    ]
