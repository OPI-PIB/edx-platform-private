# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-09-10 12:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0017_auto_20180820_1733'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseoverview',
            name='timetable',
            field=models.TextField(null=True),
        ),
    ]
