# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-08-14 16:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_admin', '0007_delete_historical_api_records'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apiaccessrequest',
            name='reason',
            field=models.TextField(help_text='Pow\xf3d dla kt\xf3rego u\u017cytkownik \u017c\u0105da dost\u0119pu do API.'),
        ),
        migrations.AlterField(
            model_name='apiaccessrequest',
            name='status',
            field=models.CharField(choices=[(b'pending', 'Oczekuje'), (b'denied', 'Odrzucony'), (b'approved', 'Zatwierdzony')], db_index=True, default=b'pending', help_text='Stan tego \u017c\u0105dania dost\u0119pu do API', max_length=255),
        ),
        migrations.AlterField(
            model_name='apiaccessrequest',
            name='website',
            field=models.URLField(help_text='Adres strony www powi\u0105zanej z tym u\u017cytkownikiem API.'),
        ),
    ]
