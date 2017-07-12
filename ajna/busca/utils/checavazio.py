# -*- coding: utf-8 -*-
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from scipy import misc
from ajna.settings import BASE_DIR
import os

n_bins = 32
histograms = pickle.load(open(os.path.join(BASE_DIR, 'busca', 'utils', 'histograms.pkl'), "rb"))
labels = pickle.load(open(os.path.join(BASE_DIR, 'busca', 'utils', 'labels.pkl'), "rb"))
clf = RandomForestClassifier()
clf.fit(histograms, labels)

def hist(img):
    histo = np.histogram(img, bins=n_bins, density=True)
    return histo[0]

def vaziooucheio(file):
    cc = misc.imread(file)
    return clf.predict([hist(cc)])

def vaziooucheiodescritivo(filepath):
    teste = vaziooucheio(filepath)
    if teste[0] == 0:
        return "Contêiner avaliado como VAZIO"
    else:
        return "Contêiner avaliado como NÃO VAZIO"
