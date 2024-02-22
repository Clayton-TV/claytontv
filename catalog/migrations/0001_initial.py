# Generated by Django 5.0.2 on 2024-02-22 18:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('summary', models.TextField(blank=True, max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter a topic or theme', max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('bio', models.TextField(max_length=1000)),
                ('series', models.ManyToManyField(to='catalog.series')),
            ],
        ),
        migrations.AddField(
            model_name='series',
            name='topic',
            field=models.ManyToManyField(to='catalog.topic'),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('summary', models.TextField(help_text='Enter a brief description of the video', max_length=1000)),
                ('series_number', models.IntegerField(blank=True, help_text='If part of a series provide the number in the series', null=True)),
                ('date_created', models.DateField()),
                ('livestream_date', models.DateField(blank=True, null=True)),
                ('embedding_url', models.URLField(unique=True)),
                ('channel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='catalog.channel')),
                ('series', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='catalog.series')),
                ('speaker', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='catalog.speaker')),
                ('topic', models.ManyToManyField(help_text='Select topics for this video', to='catalog.topic')),
            ],
            options={
                'ordering': ['date_created'],
            },
        ),
    ]
