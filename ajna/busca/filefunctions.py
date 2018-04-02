from PIL import Image
import os
import glob
# from scipy import misc
import xml.etree.ElementTree as ET
import fnmatch
from shutil import copyfile
import time
from datetime import datetime
from django.db import IntegrityError


"""
def loadimages(path, input):
    numarquivos = int(len([name for name in os.listdir(path) if name.endswith('jpg')]))
    X = np.ndarray(shape=(numarquivos, input), dtype=np.float32)
    names = np.empty(shape=(numarquivos), dtype=np.object_)
    cont = 0
    for file in glob.glob(os.path.join(path,'*.jpg')):
        im = Image.open(file)
        X[cont] = np.asarray(im).reshape(input)
        #print(file)
        names[cont]=file
        cont +=1

    return X, names

        
def loadimagesnames(path, input):
    numarquivos = int(len([name for name in os.listdir(path) if name.endswith('jpg')]))
    names = np.empty(shape=(numarquivos), dtype=np.object_)
    cont = 0
    for file in glob.glob(os.path.join(path,'*.jpg')):
        names[cont]=file
        cont +=1

    return names

def resize(file, size):
    im = Image.open(file)
    im.thumbnail(size, Image.ANTIALIAS)
    im.save(file, "JPEG")


def recortaesalva(ofile, size, odest):
        print("**"+ofile)
        im = misc.imread(ofile, True)
        yfinal, xfinal = im.shape
        ymeio = round(yfinal / 2)
        xmeio = round(xfinal / 2)
        #primeiro achar o Teto do contêiner. Tentar primeiro exatamente no meio
        yteto = 0
        for s in range(0, ymeio):
            if (im[s, xmeio] < 230):
                yteto = s
                break
        #Depois de achado o teto, percorrer as laterais para achar os lados
        xesquerda = 0
        for r in range(0, xmeio):
            if (im[yteto+5, r] < 230):
                xesquerda = r
                break
        xdireita = xfinal - 1
        for r in range(xfinal-1, xmeio, -1):
            if (im[yteto+5, r] < 215):
                xdireita = r
                break
        #Achar o piso do contêiner é bem mais difícil... Pensar em como fazer depois Talvez o ponto de max valores
        imbaixo = im[ymeio:yfinal, xesquerda:xdireita]
        ychao = imbaixo.sum(axis=1).argmin()
        ychao = ychao + ymeio + 10
        #Por fim, fazer umas correções se as medidas achadas forem absurdas
        if (ychao>yfinal):
            ychao = yfinal
        if ((xdireita-xesquerda) < (xfinal/4)):
            xdireita = xfinal - 5
            xesquerda = 5
        if (yteto == ymeio):
            yteto = 5
        imcortada = im[yteto:ychao, xesquerda:xdireita]
        filename = os.path.basename(ofile)
        destdir = os.path.dirname(odest)
        destfile = destdir+'tmp_'+filename
        print("*OFILE"+odest)
        print("*DEST*"+destfile)
        misc.imsave(destfile, imcortada)
        im = Image.open(destfile)
        imnova = im.resize(size)
        imnova.save(odest, quality=100)
        os.remove(destfile)
        return imnova
"""

def carregaarquivos(homedir, caminho, size, fonteimagem):
    path = os.path.join(fonteimagem.caminho, caminho)
    pathdest = os.path.join(homedir, 'static', 'busca')
    print('path', path)
    numero = None
    mensagem = ''
    erro = False
    from .models import ConteinerEscaneado
    try:
        for result in glob.iglob(path):
            for dirpath, dirnames, files in os.walk(result):
                for f in fnmatch.filter(files, '*.xml'):
                    print('carregaarquivos - f', f)
                    print('carregaarquivos - dir path', dirpath)
                    tree = ET.parse(os.path.join(dirpath, f))
                    root = tree.getroot()
                    for tag in root.iter('ContainerId'):
                        lnumero = tag.text
                        if lnumero is not None:
                            print("Numero")
                            print(lnumero)
                            numero = lnumero.replace('?', 'X')
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
                        print('destcompleto', destcompleto)
                        print('destparcial', destparcial)
                        try:
                            os.makedirs(destcompleto)
                        except FileExistsError as e:
                            erro = True
                            mensagem = mensagem + \
                            destcompleto + ' já existente.\n'
                            print(destcompleto, 'já existente')
                            continue
                        copyfile(os.path.join(dirpath, f), os.path.join(destcompleto, f))
                        for file in glob.glob(os.path.join(dirpath,'*mp.jpg')):
                            name = os.path.basename(file)
                            print(name)
                            copyfile(file, os.path.join(destcompleto, name))
                            # recortaesalva(file, size, os.path.join(destcompleto, numero+'.jpg'))
                            c = ConteinerEscaneado()
                            c.numero = numero
                            # c.arqimagem = destparcial+'/'+numero+'.jpg'
                            c.arqimagemoriginal = destparcial+'/'+name
                            c.fonte = fonteimagem
                            c.pub_date = data
                            mdate = time.localtime(os.path.getmtime(file))
                            mdate = time.strftime('%Y-%m-%d %H:%M:%S%z', mdate)
                            cdate = time.localtime(os.path.getctime(file))
                            cdate = time.strftime('%Y-%m-%d %H:%M:%S%z', cdate)
                            c.file_mdate = mdate
                            c.file_cdate = cdate #time.localtime(os.path.getctime(file)).strftime('%Y-%m-%d %H:%M:%S')
                            print(c.pub_date, c.file_mdate, c.file_cdate)
                            c.truckid = truckid
                            c.exportado = 0
                            try:
                                c.save()
                                # mensagem = mensagem + numero + " incluído"
                            except IntegrityError as e:
                                erro = True
                                mensagem = mensagem + path + numero + ' já cadastrado?!\n'
                        numero = None
    except Exception as err:
        raise(err)
        erro = True
        mensagem = str(err)
    return mensagem, erro

    


