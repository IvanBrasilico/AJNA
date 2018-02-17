# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-02-17 14:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('busca', '0025_auto_20180217_1234'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conteinerescaneado',
            name='file_date',
        ),
        migrations.AddField(
            model_name='conteinerescaneado',
            name='file_cdate',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data da criação do arquivo (Windows)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='conteinerescaneado',
            name='file_mdate',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data da última modificação do arquivo'),
            preserve_default=False,
        ),
    ]
