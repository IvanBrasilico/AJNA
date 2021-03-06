from django.shortcuts import render, render_to_response, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext
from django.http import JsonResponse
# Create your views here.
from django.views import generic
from django.db import transaction
from .models import FonteImagem, ConteinerEscaneado, Agendamento, exporta_bson, trata_agendamentos
import csv
from io import StringIO
import locale
locale.setlocale(locale.LC_ALL, '')
import collections
import shutil
import time
import io
from datetime import datetime
import os
import sqlite3
import matplotlib.pyplot as plt

# Inicialização/configuração - depois COLOCAR EM ARQUIVO ESPECÍFICO

size = (256, 120)
homedir = os.path.dirname(os.path.abspath(__file__))


def indexview(request):
    FonteImagem_list = FonteImagem.objects.all().order_by('nome')
    Agregadolist = ConteinerEscaneado.getTotalporFonteImagem()
    total = ConteinerEscaneado.getTotal()
    agendamentos = Agendamento.agendamentos_programados()
    percentuais = {}
    for o in Agregadolist:
        percentual = int((o['fcount'] / total) * 200)  # 600 = px para exibição
        fonte = FonteImagem.objects.get(pk=o['fonte'])
        percentuais.update({fonte.nome: percentual})
    percentuais = collections.OrderedDict(
        sorted(percentuais.items(), key=lambda t: t[0]))
    print(percentuais)
    return render(request, 'busca/index.html',
                  {'FonteImagem_list': FonteImagem_list,
                   'agendamentos': agendamentos,
                   'percentuais': percentuais,
                   'total': total})


class FonteDetailView(generic.DetailView):
    model = FonteImagem
    template_name = 'busca/detail.html'


def conteinerdetail(request, pk):
    conteiner = get_object_or_404(ConteinerEscaneado, pk=pk)
    return render(request, 'busca/conteinerdetail.html', {'conteinerescaneado': conteiner})


def paginatorconteiner(request, ConteinerEscaneado_list, template, numero="", datainicial="", datafinal="", operador="", img="", alerta="", img_page=12):
    # Show 12 images per page
    if img_page > 50:
        img_page = 50
    paginator = Paginator(ConteinerEscaneado_list, img_page)
    page = request.GET.get('page')
    try:
        conteineres = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        conteineres = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        conteineres = paginator.page(paginator.num_pages)
    context = {'conteineres': conteineres, 'numero': numero, 'datainicial': datainicial,
               'datafinal': datafinal, 'operador': operador, 'alerta': alerta}
    return render(request, template, context)


# Recebe uma imagem via form HTML e monta listaordenada dos contêineres escaneados
def filtraconteiner(request, numero="", datainicial="", datafinal="", operador="", alerta='0'):
    ConteinerEscaneadol = ConteinerEscaneado.objects.all()
    if not operador == "":
        ConteinerEscaneadol = ConteinerEscaneadol.filter(
            operador__startswith=operador)
    if not alerta == '0':
        ConteinerEscaneadol = ConteinerEscaneadol.filter(
            alerta__startswith=alerta)
    if not numero == "":
        ConteinerEscaneadol = ConteinerEscaneadol.filter(
            numero__startswith=numero)
    if not ((datainicial == "") or (datafinal == "")):
        ConteinerEscaneadol = ConteinerEscaneadol.filter(
            pub_date__range=(datainicial, datafinal+' 23:59'))
    return ConteinerEscaneadol

def buscaconteiner(request):
    numero = ""
    datainicial = ""
    datafinal = ""
    operador = ""
    alerta = ""
    if request.POST:
        numero = request.POST['numero']
        datainicial = request.POST['datainicial']
        datafinal = request.POST['datafinal']
        operador = request.POST['operador']
        alerta = request.POST['alerta']
    ConteinerEscaneadol = filtraconteiner(
        request, numero, datainicial, datafinal, operador, alerta)
    return paginatorconteiner(request, ConteinerEscaneadol.order_by('-pub_date', 'numero'), 'busca/buscaconteiner.html', numero, datainicial, datafinal, operador, alerta)


def buscaimagem(request):
    if request.POST:
        try:
            numero = request.POST['numero']
        except:
            numero = ""
        datainicial = request.POST['datainicial']
        datafinal = request.POST['datafinal']
        operador = request.POST['operador']
        alerta = 1 if 'alerta' in request.POST else 0
    ConteinerEscaneadol = filtraconteiner(
        request, numero, datainicial, datafinal, operador, alerta)
    img_per_page = len(ConteinerEscaneadol) if ConteinerEscaneadol else 1
    return paginatorconteiner(request, ConteinerEscaneadol.order_by('-pub_date', 'numero'), 'busca/buscaconteiner.html', numero, datainicial, datafinal, operador, alerta, img_page=img_per_page)


def trataagendamentos(request):
    trata_agendamentos()
    return render_to_response('busca/index.html',
                              {'mensagem': 'Agendamentos processados - ver log'})


@transaction.atomic
def exportabson(request):
    batch_size = request.GET.get('batch_size')
    if batch_size:
        batch_size = int(batch_size)

    dict_export, name, qtde = exporta_bson(batch_size)
    if dict_export:
        mensagem = (str(qtde) + ' imagens exportadas junto com XML correspondente'
                ' para o arquivo ../files/BSON/' + name)
    else:
        mensagem = 'Função retornou apenas '
    return render_to_response('busca/index.html',
                              {'mensagem': mensagem})

def zerabson(request):
    ConteinerEscaneado.objects.all().filter(exportado=1).update(exportado=0)
    return render_to_response('busca/index.html')

