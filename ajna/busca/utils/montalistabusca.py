# -*- coding: utf-8 -*-

from ..indexfunctions import montaListaOrdenadaEuclidean
import sqlite3 as sql
import numpy as np
from PIL import Image
import pickle

def compressedimg(image, encoding_model):
    image = image.resize((256,120), Image.ANTIALIAS)
    imageSearch = np.asarray(image).reshape(256*120)
    imageSearch = imageSearch / 255
    return np.array(encoding_model.predict([imageSearch]), dtype=np.float32)

def montaorder(image, encoding_model):
    con = sql.connect('db.sqlite3',isolation_level=None)
    cur = con.cursor()
    compressedSearch = compressedimg(image, encoding_model)
    print(compressedSearch)
    #print('compressedSearch')
    #print(compressedSearch)
    cur.execute("SELECT codigoplano FROM busca_conteinerescaneado WHERE codigoplano is not null")
    data = cur.fetchall()
    imagelistSearch = np.empty((len(data), 200))
    for r in range(0, len(data)):
        imageCompressed = np.array(pickle.loads(data[r][0]), dtype=np.float32)
        #print('imageCompressed')
        #print(imageCompressed)
        imagelistSearch[r] = imageCompressed
    order = montaListaOrdenadaEuclidean(imagelistSearch, compressedSearch)
    print("Ordem:")
    print(order)
    return order

def ordenalista(image, encoding_model, lista):
    compressedSearch = compressedimg(image, encoding_model)
    print(compressedSearch)
    nregistros = len(lista)
    imagelistSearch = np.empty((nregistros, 200))
    for r in range(0, nregistros):
        imageCompressed = np.array(pickle.loads(lista[r].codigoplano), dtype=np.float32)
        imagelistSearch[r] = imageCompressed
    order = montaListaOrdenadaEuclidean(imagelistSearch, compressedSearch)
    return order
    
    

