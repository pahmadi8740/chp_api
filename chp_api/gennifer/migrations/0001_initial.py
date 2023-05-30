# Generated by Django 4.2.1 on 2023-05-29 22:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Algorithm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('run_url', models.URLField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('title', models.CharField(max_length=128)),
                ('zenodo_id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('doi', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True, null=True)),
                ('upload_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Gene',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('curie', models.CharField(max_length=128)),
                ('variant', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InferenceStudy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('max_study_edge_weight', models.FloatField(null=True)),
                ('min_study_edge_weight', models.FloatField(null=True)),
                ('avg_study_edge_weight', models.FloatField(null=True)),
                ('std_study_edge_weight', models.FloatField(null=True)),
                ('is_public', models.BooleanField(default=False)),
                ('status', models.CharField(max_length=10)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('algorithm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='studies', to='gennifer.algorithm')),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='studies', to='gennifer.dataset')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='studies', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InferenceResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('edge_weight', models.FloatField()),
                ('is_public', models.BooleanField(default=False)),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='gennifer.inferencestudy')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inference_result_target', to='gennifer.gene')),
                ('tf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inference_result_tf', to='gennifer.gene')),
            ],
        ),
    ]
