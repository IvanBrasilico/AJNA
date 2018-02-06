# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-07 19:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('busca', '0018_auto_20170807_1642'),
    ]

    operations = [
        migrations.AddField(
            model_name='conteinerescaneado',
            name='login',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddIndex(
            model_name='conteinerescaneado',
            index=models.Index(fields=['login'], name='busca_conte_login_7fc817_idx'),
        ),
    ]
