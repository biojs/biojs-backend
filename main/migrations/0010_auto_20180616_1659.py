# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-16 16:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20180609_0855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contribution',
            name='component',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contributions', to='main.Component'),
        ),
    ]
