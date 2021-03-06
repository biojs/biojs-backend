# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-05-28 21:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contributions', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Contributor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('avatar_url', models.URLField()),
            ],
        ),
        migrations.AddField(
            model_name='component',
            name='commits',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='component',
            name='forks',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='component',
            name='no_of_contributors',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='component',
            name='no_of_releases',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='component',
            name='open_issues',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='component',
            name='version',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='component',
            name='wwatchers',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='contributor',
            name='components',
            field=models.ManyToManyField(through='main.Contribution', to='main.Component'),
        ),
        migrations.AddField(
            model_name='contribution',
            name='component',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.Component'),
        ),
        migrations.AddField(
            model_name='contribution',
            name='contributor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.Contributor'),
        ),
    ]
