from django.shortcuts import render, render_to_response, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext
from django.http import JsonResponse
# Create your views here.
from django.views import generic
from django.db import transaction
from .models import FonteImagem, ConteinerEscaneado, Agendamento, exporta_bson
import csv
from io import StringIO
import locale
locale.setlocale(locale.LC_ALL, '')
import collections
import shutil

import io
from datetime import datetime
import os
import sqlite3

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
        percentual = int((o['fcount'] / total) * 600)  # 600 = px para exibição
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


def paginatorconteiner(request, ConteinerEscaneado_list, template, numero="", datainicial="", datafinal="", login="", img="", alerta=""):
    # Show 12 images per page
    paginator = Paginator(ConteinerEscaneado_list, 12)
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
               'datafinal': datafinal, 'login': login, 'alerta': alerta}
    return render(request, template, context)


# Recebe uma imagem via form HTML e monta listaordenada dos contêineres escaneados
def filtraconteiner(request, numero="", datainicial="", datafinal="", login="", alerta=""):
    ConteinerEscaneadol = ConteinerEscaneado.objects.all()
    if not login == "":
        ConteinerEscaneadol = ConteinerEscaneadol.filter(
            login__startswith=login)
    if not alerta == "":
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
    login = ""
    alerta = ""
    if request.POST:
        numero = request.POST['numero']
        datainicial = request.POST['datainicial']
        datafinal = request.POST['datafinal']
        login = request.POST['login']
        alerta = request.POST['alerta']
    ConteinerEscaneadol = filtraconteiner(
        request, numero, datainicial, datafinal, login, alerta)
    return paginatorconteiner(request, ConteinerEscaneadol.order_by('-pub_date', 'numero'), 'busca/buscaconteiner.html', numero, datainicial, datafinal)


def buscaimagem(request):
    numero = ""
    datainicial = ""
    datafinal = ""
    login = ""
    alerta = ""
    if request.POST:
        try:
            numero = request.POST['numero']
        except:
            numero = ""
        if not numero == "":
            datainicial = request.POST['datainicial']
            datafinal = request.POST['datafinal']
            login = request.POST['login']
            alerta = request.POST['alerta']
    ConteinerEscaneadol = filtraconteiner(
        request, numero, datainicial, datafinal, login, alerta)
    return paginatorconteiner(request, ConteinerEscaneadol, 'busca/buscaconteiner.html', numero, datainicial, datafinal, login, alerta)


@transaction.atomic
def exportaimagens(request):
    batch_size = request.GET.get('batch_size')
    if batch_size:
        batch_size = int(batch_size)

    dict_export, name, qtde = exporta_bson(batch_size)
    mensagem = (str(qtde) + ' imagens exportadas junto com XML correspondente'
                ' para o arquivo ../files/BSON/' + name)
    return render_to_response('busca/index.html',
                              {'mensagem': mensagem})
