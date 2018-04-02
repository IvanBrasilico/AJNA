# -*- coding: utf-8 -*-
"""
This module allows counting, using the XML info, the quantity of xml
archives in a path. The code must be sync with carrega_arquivos.

Created on Mon Apr  2 14:50:36 2018

@author: alfts
"""
import datetime
import glob
import fnmatch
import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from .models import Agendamento

def conta_dir(path):
    """Percorre diretórios de contêineres, abre XML, conta xml válidos.
    
    XML válido = verificações que são feitas no carrega_arquivos
    Tem a estrutura esperada?
    Tem um numero?

    """
    counter = Counter()
    # print('path', path)
    numero = None
    for result in glob.iglob(path):
        for dirpath, dirnames, files in os.walk(result):
            for f in fnmatch.filter(files, '*.xml'):
                tree = ET.parse(os.path.join(dirpath, f))
                root = tree.getroot()
                for tag in root.iter('ContainerId'):
                    lnumero = tag.text
                    if lnumero is not None:
                        numero = lnumero
                for tag in root.iter('Date'):
                    data=tag.text
                if numero is not None:
                    ano = data[:4]
                    mes = data[5:7]
                    dia = data[8:10]
                    counter[ano+mes+dia] += 1
    return counter

def conta_por_agendamento():
    lista_agendamentos = Agendamento.objects.all()
    for ag in lista_agendamentos:
        fonte = ag.fonte
        data = datetime.datetime(2018, 1, 1)
        caminho = data.strftime(ag.mascarafiltro)
        homedir = fonte.caminho
        path = os.path.join(homedir, caminho)
        print(path, conta_dir(path))
        

if __name__=='__main__':
    # TODO: Call like trata_agendamento, using information from Models
    # caminho = 'P:\\ECOPORTO\\ECOPORTO_ORDENADO\\'
    # path = os.path.join(caminho, '2017', '02', '16')
    conta_por_agendamento()


