# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-07 18:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('busca', '0016_auto_20170807_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conteinerescaneado',
            name='login',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
