# Generated by Django 2.0.3 on 2018-04-05 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('busca', '0026_auto_20180217_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='conteinerescaneado',
            name='alerta',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='conteinerescaneado',
            name='operador',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='conteinerescaneado',
            name='arqimagem',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='conteinerescaneado',
            name='arqimagemoriginal',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='conteinerescaneado',
            name='truckid',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]