# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-07 19:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('busca', '0017_auto_20170807_1525'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='conteinerescaneado',
            name='busca_conte_login_7fc817_idx',
        ),
        migrations.RemoveField(
            model_name='conteinerescaneado',
            name='login',
        ),
    ]
