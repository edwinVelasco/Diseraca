# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-12-06 19:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Diseraca', '0002_auto_20171008_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='prestamo',
            name='matriculados',
            field=models.IntegerField(default=12),
            preserve_default=False,
        ),
    ]
