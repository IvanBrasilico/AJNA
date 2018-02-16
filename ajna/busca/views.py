from django.shortcuts import render, render_to_response, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext
from django.http import JsonResponse
# Create your views here.
from django.views import generic
from .models import FonteImagem, ConteinerEscaneado, Agendamento, exporta_arquivos
from .forms import ImageUploadForm
import csv
from io import StringIO
import pandas as pd
import locale
locale.setlocale(locale.LC_ALL, '')
import collections
import zipfile as zipf
import shutil

from PIL import Image
import numpy as np
import io
from datetime import datetime
import pickle
import os
import sqlite3

# Inicialização/configuração - depois COLOCAR EM ARQUIVO ESPECÍFICO
from .utils import checavazio
from .utils import predizpeso
from .utils import montalistabusca

size = (256, 120)
homedir = os.path.dirname(os.path.abspath(__file__))

"""
import tflearn
from .modelfully import modelfully1
inputsize = int(size[0]*size[1])
model, encoder, decode = modelfully1(inputsize)
global homedir
modeldir = os.path.join(homedir, 'plano', 'conteineresencoder.tflearn' )
model.load(modeldir)
global encoding_model
encoding_model = tflearn.DNN(encoder, session=model.session)
print("Modelo carregado")
global order
global imgsimilar
staticdir = os.path.join(homedir, 'static/busca')
order = None
imgsimilar = None
"""


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
    testavazio = checavazio.vaziooucheiodescritivo(
        os.path.join(homedir, "static/busca/", conteiner.arqimagem))
    return render(request, 'busca/conteinerdetail.html', {'conteinerescaneado': conteiner, 'testavazio': testavazio})


def frmimagem(request):  # Formulário para fazer UPLOAD de imagem a buscar
    return render(request, 'busca/frmimagem.html')


def frmcomparapesos(request):  # Formulário para fazer UPLOAD de CSV a buscar
    return render(request, 'busca/frmcomparapesos.html')


def frmlistavazios(request):  # Formulário para fazer UPLOAD de CSV a buscar
    return render(request, 'busca/frmlistavazios.html')


def frmcompactandoarquivos(request):  # Formulário para COMPACTAR arquivos
    return render(request, 'busca/frmcompactandoarquivos.html')


def frmdescompactandoarquivos(request):
    return render(request, 'busca/frmdescompactandoarquivos.html')


def listavazios(request):  # Trata UPLOAD de CSV
    mensagem = ""
    if request.POST and request.FILES:
        csvfile = request.FILES['csv']
        datainicial = request.POST['datainicial']
        datafinal = request.POST['datafinal']
        csvf = StringIO(csvfile.read().decode())
        reader = csv.reader(csvf)
        listavazios = []
        listanaovazios = []
        listanaoencontrados = []
        for row in reader:
            print(row)
            conteineres_list = ConteinerEscaneado.objects.all(
            ).filter(pub_date__range=(datainicial, datafinal+' 23:59'),
                     numero=row[0])
            if len(conteineres_list) == 0:
                listanaoencontrados.append(row[0])
            else:
                for conteiner in conteineres_list:
                    teste = checavazio.vaziooucheio(os.path.join(staticdir,
                                                                 conteiner.arqimagem))
                    if teste == [0]:
                        listavazios.append(conteiner)
                    else:
                        listanaovazios.append(conteiner)
        total = len(listavazios)+len(listanaovazios)+len(listanaoencontrados)
        percvazios = int((len(listavazios) / total) * 600)  # 200 = px
        percnvazios = int((len(listanaovazios) / total) * 600)  # 200 = px
        percnencontrados = int(
            (len(listanaoencontrados) / total) * 600)  # 200 = px

    return render(request, 'busca/listavazios.html', {'mensagem': mensagem,
                                                      'listavazios': listavazios,
                                                      'listanaovazios': listanaovazios,
                                                      'listanaoencontrados': listanaoencontrados,
                                                      'percvazios': percvazios,
                                                      'percnvazios': percnvazios,
                                                      'percnencontrados': percnencontrados})


def comparapesos(request):  # Trata UPLOAD de CSV
    mensagem = ""
    if request.POST and request.FILES:
        csvade = request.FILES['pesosADE']
        csva = StringIO(csvade.read().decode())
        dfa = pd.read_csv(
            csva, names=['Contêiner', 'B - Peso verificado em balança'])
        csvcarga = request.FILES['pesosCarga']
        datainicial = request.POST['datainicial']
        datafinal = request.POST['datafinal']
        csvc = StringIO(csvcarga.read().decode())
        dfc = pd.read_csv(
            csvc, names=['Contêiner', 'A - Peso declarado Sistema Carga'])
        df = pd.merge(dfc, dfa, how='outer')
        df['A-B'] = df['A - Peso declarado Sistema Carga'] - \
            df['B - Peso verificado em balança']
        df['C - Peso estimado pela imagem'] = np.nan
        cont = 0
        pesoestimado = 0
        for num in df['Contêiner']:
            try:
                conteiner = ConteinerEscaneado.objects.get(numero=num).filter(pub_date__range=(datainicial, datafinal+' 23:59'),
                                                                              numero=num[0])
                df['Contêiner'][cont] = "<a href=\"/busca/conteiner/" + \
                    str(conteiner.id)+"/\">"+df['Contêiner'][cont]+"</a>"
                pesoestimado = predizpeso.pesoimagem(os.path.join(
                    homedir, "static/busca/", conteiner.arqimagem))
                print('Peso estimado:' + str(pesoestimado))
                df['C - Peso estimado pela imagem'][cont] = pesoestimado
            except:
                pass
            cont += 1
        df['A-C'] = df['A - Peso declarado Sistema Carga'] - \
            df['C - Peso estimado pela imagem']
        df['%%%'] = (abs(df['A-C'])+abs(df['A-B'])) / \
            (df['A - Peso declarado Sistema Carga']*2)
        df.sort_values('%%%', ascending=False,
                       inplace=True, na_position='first')
        df = df.fillna('Não encontrado!!!')
        html_table = df.to_html(index=False, escape=False,
                                float_format="{0:.2f}".format)
        print("Pandas enviado!!!")
        print(df)
        # print(html_table)
    else:
        mensagem = "Arquivos de peso declarado e balanças não enviados!"
    return render_to_response('busca/comparacaodepesos.html', {'mensagem': mensagem, 'html_table': html_table}, RequestContext(request))


def buscasimilar(request, pk):
    global order
    global imgsimilar
    conteiner = get_object_or_404(ConteinerEscaneado, pk=pk)
    img = Image.open(os.path.join(
        homedir, "static/busca/", conteiner.arqimagem))
    order = montalistabusca.montaorder(img, encoding_model)
    imgsimilar = img
    return buscaimagem(request)


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


# Recebe uma imagem via form HTML e monta listaordenada dos contêineres escaneados
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
    else:  # Chamou a primeira vez,  inicialização!
        global order
        order = None  # Reiniciafiltragem
        # Pensar em inicializar datainicial em alguns meses ou um ano atrás para economizar recursor
        #
        #
    ConteinerEscaneadol = filtraconteiner(
        request, numero, datainicial, datafinal, login, alerta)
    # , login)
    return paginatorconteiner(request, list(ConteinerEscaneadol.order_by('-pub_date', 'numero')), 'busca/buscaconteiner.html', numero, datainicial, datafinal)


# Recebe uma imagem via form HTML e monta listaordenada dos contêineres escaneados
def buscaimagem(request):
    global order
    global imgsimilar
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
    if request.POST:
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            buf = request.FILES['image'].read()
            img = Image.open(io.BytesIO(buf)).convert('L')
            print("Shape")
            print(img.size)
            img = img.resize(size)
            print(img.size)
            imgsimilar = img
            order = montalistabusca.ordenalista(
                imgsimilar, encoding_model, ConteinerEscaneadol)
            # order = montalistabusca.montaorder(img, encoding_model)
    ConteinerEscaneado_list = []
    if order is not None:
        print("Ordenando...")
        if len(order) != len(ConteinerEscaneadol):  # Filtrado, reindexar
            print("Lista filtrada...")
            order = montalistabusca.ordenalista(
                imgsimilar, encoding_model, ConteinerEscaneadol)
        ConteinerEscaneadol = list(ConteinerEscaneadol)
        for index in order:
            ConteinerEscaneado_list.append(ConteinerEscaneadol[index])
        # print('ordered')
        # print(ConteinerEscaneado_list[0])
    else:
        ConteinerEscaneado_list = list(
            ConteinerEscaneadol.order_by('-pub_date', 'numero'))
        # print('not ordered')
        # print(ConteinerEscaneado_list[0])
    return paginatorconteiner(request, ConteinerEscaneado_list, 'busca/buscaconteiner.html', numero, datainicial, datafinal, login, alerta)


from django.db import transaction


@transaction.atomic
def indexar(request):
    # conteineressemcodigo = ConteinerEscaneado.objects.filter(codigoplano__isnull="True")
    conteineressemcodigo = ConteinerEscaneado.objects.all()
    for c in conteineressemcodigo:
        img = Image.open(os.path.join(staticdir, c.arqimagem))
        X = np.asarray(img).reshape(inputsize)
        X = X / 255
        compressed = np.array(encoding_model.predict([X]), dtype=np.float32)
        c.codigoplano = pickle.dumps(compressed)
        c.save()
    return render_to_response('busca/index.html', {'mensagem': 'Indexação realizada!', 'FonteImagem_list': FonteImagem.objects.all()})


def carregaimagens(request):
    fonteimagem = FonteImagem.objects.get(pk=request.POST['fonteimagem'])
    caminho = request.POST['caminho']
    from .filefunctions import carregaarquivos
    mensagem = carregaarquivos(homedir, caminho, size, fonteimagem)
    return render_to_response('busca/index.html',
                              {'mensagem': mensagem, 'FonteImagem_list': FonteImagem.objects.all()})

# from django.db import transaction
#@transaction.atomic


def indexarold(request):
    from .filefunctions import loadimages
    X, names = loadimages(
        '/home/ivan/Estudo/NanoDegree/ajna/busca/static/busca', inputsize)
    X = X / 255
    compressed = np.array(encoding_model.predict(X), dtype=np.float32)
    # print(compressed[0])
    import sqlite3 as sql
    con = sql.connect('db.sqlite3', isolation_level=None)
    cur = con.cursor()
    f = FonteImagem.objects.all().get(id=1)
    cont = 0
    cur.execute("BEGIN")
    name = names[0]
    for name in names:
        # print(name)
        # c = ConteinerEscaneado()
        arqimagem = name[-15:]
        numero = arqimagem[:11]
        fonte = f.id
        # c.codigoplano=pickle.dumps(compressed[cont])
        pub_date = datetime.now()
        # c.save()
        cur.execute("INSERT INTO busca_conteinerescaneado (numero, pub_date, arqimagem, fonte_id, codigoplano) VALUES (?,?,?,?,?)",
                    (numero, pub_date, arqimagem, fonte, pickle.dumps(compressed[cont])))
        cont += 1
    cur.execute("END")
    # transaction.commit()
    return render_to_response('busca/index.html', {'mensagem': 'Indexação realizada!', 'FonteImagem_list': FonteImagem.objects.all()})


def compactandoarquivos(request):
    mensagem = ""
    if request.POST:
        bd = 'db_dump.sqlite3'
        imagens = 'busca\\static\\busca\\2017'
        with zipf.ZipFile('BancoDadoseImag.zip', 'w', zipf.ZIP_DEFLATED) as z:
            for folder, subfolders, files in os.walk(imagens):
                for file in files:
                    z.write(os.path.join(folder, file), os.path.relpath(os.path.join(
                        folder, file), 'D:\\Users\\47020753817\\Downloads\\WinPython-64bit-3.5.3.1Qt5\\AJNA\\ajna\\busca\\static\\busca'), compress_type=zipf.ZIP_DEFLATED)
        z.close()
        print("Imagens compactadas!")
        dumpBD()
        with zipf.ZipFile('BancoDadoseImag.zip', 'a', zipf.ZIP_DEFLATED) as z:
            z.write(bd)
        z.close()
        print("Banco compactado!")
    else:
        mensagem = "Arquivos não enviados!"
    return render_to_response('busca/frmcompactandoarquivos.html', {'mensagem': mensagem},
                              RequestContext(request))


def dumpBD():  # realiza o backup do banco de dados
    conn = sqlite3.connect('db.sqlite3')
    with io.open('db_dump.sqlite3', 'w') as f:
        for linha in conn.iterdump():
            f.write('%s\n' % linha)
    print('Backup realizado com sucesso.')
    print('Salvo como db_dump.sqlite3')
    conn.close()


def descompactaarquivos(request):
    mensagem = ""
    if request.POST:
        with zipf.ZipFile('BancoDadoseImag.zip', 'r', zipf.ZIP_DEFLATED) as z:
            z.extractall()
        z.close()
        recDump()
        # moveArquivos()
    else:
        mensagem = "Arquivos não enviados!"
    return render_to_response('busca/frmdescompactandoarquivos.html', {'mensagem': mensagem},
                              RequestContext(request))


def moveArquivos():
    src = 'D:\\'
    dst = 'D:\\'

    print(os.listdir(src))
    print(os.listdir(dst))
    for file in os.listdir(src):
        if file not in os.listdir(dst):
            print(file)  # testing
            src_file = os.path.join(src, file)
            dst_file = os.path.join(dst, file)
            shutil.move(src_file, dst_file)
    else:
        pass


def recDump():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    f = io.open('db_dump.sqlite3', 'r')
    sqlite = f.read()
    cursor.executescript(sqlite)
    print('Dump realizado')
    conn.close()


@transaction.atomic
def exportaimagens(request):
    batch_size = request.GET.get('batch_size')
    dict_export, name, qtde = exporta_arquivos(batch_size)
    mensagem = (str(qtde) + ' imagens exportadas junto com XML correspondente'
                ' para o arquivo AJNA/ajna/busca/' + name)
    return render_to_response('busca/index.html',
                              {'mensagem': mensagem})
