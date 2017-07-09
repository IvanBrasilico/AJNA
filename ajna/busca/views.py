from django.shortcuts import render, render_to_response, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
# Create your views here.
from django.views import generic
from .models import FonteImagem, ConteinerEscaneado
from .forms import ImageUploadForm

from PIL import Image
import numpy as np
import io
from datetime import datetime
import pickle
import os
import fnmatch
import glob
from shutil import copyfile
import tflearn

### Inicialização/configuração - depois COLOCAR EM ARQUIVO ESPECÍFICO
from .modelfully import modelfully1
from .utils import checavazio
from .utils import montalistabusca

size = (256, 120)
inputsize = int(size[0]*size[1])
model, encoder, decoder = modelfully1(inputsize)
global homedir 
homedir = os.path.dirname(os.path.abspath(__file__))
modeldir = os.path.join(homedir, 'plano', 'conteineresencoder.tflearn' )
model.load(modeldir)
global encoding_model
encoding_model = tflearn.DNN(encoder, session=model.session)
print("Modelo carregado")   
global order
#homedir = '/home/ivan/Estudo/NanoDegree/ajna/busca/'
staticdir = os.path.join(homedir, 'static/busca')
order = None

class IndexView(generic.ListView):
    template_name = 'busca/index.html'
    context_object_name = 'FonteImagem_list'

    def get_queryset(self):
        return FonteImagem.objects.all()
        
class FonteDetailView(generic.DetailView):
    model = FonteImagem
    template_name = 'busca/detail.html'


def conteinerdetail(request, pk):
    conteiner = get_object_or_404(ConteinerEscaneado, pk=pk)
    testavazio = checavazio.vaziooucheiodescritivo(os.path.join(homedir, "static/busca/", conteiner.arqimagem))
    return render(request, 'busca/conteinerdetail.html', {'conteinerescaneado': conteiner, 'testavazio': testavazio})

def frmimagem(request): # Formulário para fazer UPLOAD de imagem a buscar
    return render(request, 'busca/frmimagem.html' )

def frmcomparapesos(request): # Formulário para fazer UPLOAD de CSV a buscar
    return render(request, 'busca/frmcomparapesos.html' )

def comparapesos(request): # Formulário para fazer UPLOAD de CSV a buscar
    return render(request, 'busca/comparapesos.html' )

def frmlistavazios(request): # Formulário para fazer UPLOAD de CSV a buscar
    return render(request, 'busca/frmlistavazios.html' )

def listavazios(request): # Formulário para fazer UPLOAD de imagem a buscar
    import csv
    from io import StringIO
    mensagem = ""
    if request.POST and request.FILES:
        csvfile = request.FILES['csv']
        csvf = StringIO(csvfile.read().decode())
        reader = csv.reader(csvf)
        listavazios = []
        listanaovazios = []
        listanaoencontrados = []
        for row in reader:
            print(row)
            listc = ConteinerEscaneado.objects.all().filter(numero=row[0])
            if len(listc) == 1:
                c = listc[0]
                teste = checavazio.vaziooucheio(os.path.join(staticdir, c.arqimagem))
                if teste == [0]:
                    listavazios.append(c)
                else:
                    listanaovazios.append(c)
            else:
                listanaoencontrados.append(row[0])
    return render(request, 'busca/listavazios.html' , {'mensagem': mensagem, 
                                                          'listavazios': listavazios,
                                                          'listanaovazios' : listanaovazios,
                                                          'listanaoencontrados': listanaoencontrados})


def buscasimilar(request,pk):
    global order
    conteiner = get_object_or_404(ConteinerEscaneado, pk=pk)
    img = Image.open(os.path.join(homedir, "static/busca/", conteiner.arqimagem))
    order = montalistabusca.montaorder(img, encoding_model)
    return buscaimagem(request)

def paginatorconteiner(request, ConteinerEscaneado_list, template, numero="", datainicial="", datafinal=""):
    paginator = Paginator(ConteinerEscaneado_list, 12) # Show 12 images per page
    page = request.GET.get('page')
    try:
        conteineres = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        conteineres = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        conteineres = paginator.page(paginator.num_pages)
    context = {'conteineres': conteineres, 'numero':numero, 'datainicial':datainicial, 'datafinal':datafinal }
    return render(request, template, context )


def filtraconteiner(request, numero="", datainicial="", datafinal=""): #Recebe uma imagem via form HTML e monta listaordenada dos contêineres escaneados
   ConteinerEscaneadol = ConteinerEscaneado.objects.all().order_by('-pub_date', 'numero')
   if not numero  == "":
       ConteinerEscaneadol = ConteinerEscaneadol.filter(numero__startswith=numero)
   if not ((datainicial == "") or (datafinal == "")):
       ConteinerEscaneadol = ConteinerEscaneadol.filter(pub_date__range=(datainicial, datafinal+' 23:59'))
   return list(ConteinerEscaneadol)

def buscaconteiner(request): #Recebe uma imagem via form HTML e monta listaordenada dos contêineres escaneados
   numero = ""
   datainicial=""
   datafinal=""
   if request.POST:
       numero = request.POST['numero']
       datainicial=request.POST['datainicial']
       datafinal=request.POST['datafinal']
   ConteinerEscaneadol = filtraconteiner(request, numero, datainicial, datafinal)
   return paginatorconteiner(request, list(ConteinerEscaneadol), 'busca/buscaconteiner.html', numero, datainicial, datafinal)


def buscaimagem(request): #Recebe uma imagem via form HTML e monta listaordenada dos contêineres escaneados
    global order
    if (request.method == 'POST'):
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            buf = request.FILES['image'].read()
            img = Image.open(io.BytesIO(buf)).convert('L')
            print("Shape")
            print(img.size)
            img = img.resize(size)
            print(img.size)
            order = montalistabusca.montaorder(img, encoding_model)
    ConteinerEscaneadol = list(ConteinerEscaneado.objects.all())
    ConteinerEscaneado_list = []
    if order is not None:
        for index in order:
            ConteinerEscaneado_list.append(ConteinerEscaneadol[index])
        #print('ordered')
        #print(ConteinerEscaneado_list[0])
    else:
        ConteinerEscaneado_list = ConteinerEscaneadol
        #print('not ordered')
        #print(ConteinerEscaneado_list[0])
    return paginatorconteiner(request, ConteinerEscaneado_list, 'busca/buscaimagem.html')


#from django.db import transaction
#@transaction.atomic
def indexarold(request):
    from .filefunctions import loadimages
    X, names = loadimages('/home/ivan/Estudo/NanoDegree/ajna/busca/static/busca', inputsize)
    X = X / 255
    compressed = np.array(encoding_model.predict(X), dtype=np.float32)
    #print(compressed[0])
    import sqlite3 as sql
    con = sql.connect('db.sqlite3',isolation_level=None)
    cur = con.cursor()
    f = FonteImagem.objects.all().get(id=1)
    cont = 0
    cur.execute("BEGIN")
    name = names[0]
    for name in names:
        #print(name)
        #c = ConteinerEscaneado()
        arqimagem = name[-15:]
        numero = arqimagem[:11]
        fonte = f.id
        #c.codigoplano=pickle.dumps(compressed[cont])
        pub_date = datetime.now()
        #c.save()
        cur.execute("INSERT INTO busca_conteinerescaneado (numero, pub_date, arqimagem, fonte_id, codigoplano) VALUES (?,?,?,?,?)",
                    (numero, pub_date, arqimagem, fonte, pickle.dumps(compressed[cont])))
        cont+=1
    cur.execute("END")

    #transaction.commit()
    return render_to_response('busca/index.html', {'mensagem': 'Indexação realizada!', 'FonteImagem_list': FonteImagem.objects.all()} )


from django.db import transaction
@transaction.atomic
def indexar(request):
    conteineressemcodigo = ConteinerEscaneado.objects.filter(codigoplano__isnull="True")
    for c in conteineressemcodigo:
        img = Image.open(os.path.join(staticdir, c.arqimagem))
        X = np.asarray(img).reshape(inputsize)
        X = X / 255
        compressed = np.array(encoding_model.predict([X]), dtype=np.float32)
        c.codigoplano =  pickle.dumps(compressed)
        c.save()
    return render_to_response('busca/index.html', {'mensagem': 'Indexação realizada!', 'FonteImagem_list': FonteImagem.objects.all()} )


def carregaimagens(request):
    fonteimagem = FonteImagem.objects.get(pk=request.POST['fonteimagem'])
    caminho = request.POST['caminho']
    from .filefunctions import carregaarquivos
    from .filefunctions import recorta
    import xml.etree.ElementTree as ET
    path = os.path.join(fonteimagem.caminho, caminho)
    pathdest = os.path.join(homedir, "static/busca/")
    print(path)
    numero = None
    mensagem = "Imagens carregadas!"
    for result in glob.iglob(path):
        for dirpath, dirnames, files in os.walk(result):
            for f in fnmatch.filter(files, '*.xml'):
                print(f)
                print(dirpath)
                tree = ET.parse(os.path.join(dirpath, f))
                root = tree.getroot()
                for tag in root.iter('ContainerId'):
                    lnumero = tag.text
                    if lnumero is not None:
                        print("Numero")
                        print(lnumero)
                        numero = lnumero
                for tag in root.iter('TruckId'):
                    truckid=tag.text
                    print(truckid)
                for tag in root.iter('Date'):
                    data=tag.text
                    print(data)
                if numero is not None:
                    print('Processando...')
                    ano = data[:4]
                    mes = data[5:7]
                    dia = data[8:10]
                    destparcial = os.path.join(ano, mes, dia, numero)
                    destcompleto = os.path.join(pathdest, destparcial)
                    print(destcompleto)
                    print(destparcial)
                    try:
                        os.makedirs(destcompleto)
                    except IOError as e:
                        print ("Unexpected error: "+e.strerror)
                        pass
                    copyfile(os.path.join(dirpath, f), os.path.join(destcompleto, f))
                    for file in glob.glob(os.path.join(dirpath,'*mp.jpg')):
                        name = os.path.basename(file)
                        print(name)
                        copyfile(file, os.path.join(destcompleto, name))
                        recortaesalva(file, size, os.path.join(destcompleto, numero+'.jpg'))
                        c = ConteinerEscaneado()
                        c.numero = numero
                        c.arqimagem = destparcial+'/'+numero+'.jpg'
                        c.arqimagemoriginal = destparcial+'/'+name
                        c.fonte = fonteimagem
                        c.pub_date = data
                        c.truckid = truckid
                        try:
                            c.save()
                            mensagem = mensagem + numero + " incluído"
                        except IntegrityError as e:
                            mensagem = mensagem + numero + " já cadastrado?!"
                            
                            
                        
                    numero = None
    return render_to_response('busca/index.html', {'mensagem': mensagem, 'FonteImagem_list': FonteImagem.objects.all()} )
