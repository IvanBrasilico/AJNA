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


def carregaarquivos(homedir, caminho, size, fonteimagem):
    path = os.path.join(fonteimagem.caminho, caminho)
    pathdest = os.path.join(homedir, 'static', 'busca')
    print('path', path)
    numero = None
    mensagem = ''
    erro = False
    alerta = False
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
                    for tag in root.iter('Date'):
                        data=tag.text
                    for tag in root.iter('Login'):
                        operador=tag.text
                    for tag in root:
                        for t in tag.getchildren():
                            if t.text == 'AL':
                                alerta = True
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
                            c.alerta = alerta
                            c.operador = operador
                            c.exportado = 0
                            try:
                                c.save()
                                # mensagem = mensagem + numero + " incluído"
                            except IntegrityError as e:
                                erro = True
                                mensagem = mensagem + path + numero + ' já cadastrado?!\n'
                        numero = None
        else:
            mensagem = mensagem + path + ' retornou lista vazia!! Sem acesso? \n'
            erro = True
    except Exception as err:
        raise(err)
        erro = True
        mensagem = str(err)
    return mensagem, erro

    


