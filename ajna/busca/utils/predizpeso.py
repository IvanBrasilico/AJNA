# -*- coding: utf-8 -*-
import pickle
import numpy as np
from sklearn import linear_model
from scipy import misc
from ajna.settings import BASE_DIR
import os

n_bins = 32
with open(os.path.join(BASE_DIR, 'busca', 'utils', "histograms.pkl"), "rb") as f:
    histograms = pickle.load(f)
    
'''cont = 0
for linha in histograms:
    linha = linha[:32]
    histograms[cont]=linha
    cont += 1
'''
labels = pickle.load(open(os.path.join(BASE_DIR, 'busca', 'utils', "labels.pkl"), "rb"))
reg = linear_model.LinearRegression()
reg.fit(histograms, labels)

def hist(img):
    histo = np.histogram(img, bins=n_bins, density=True)
    return histo[0]

def pesoimagem(filepath):
    cc = misc.imread(filepath)
    return reg.predict([hist(cc)])

    
