# Generated by Django 4.2.1 on 2023-05-29 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dispatcher', '0007_template_templatematch'),
    ]

    operations = [
        migrations.AddField(
            model_name='dispatchersettings',
            name='sri_node_normalizer_baseurl',
            field=models.URLField(default='https://nodenormalization-sri.renci.org', max_length=128),
        ),
    ]
