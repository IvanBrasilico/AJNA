# -*- coding: utf-8 -*-
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from scipy import misc

n_bins = 32
histograms = pickle.load(open("/home/ivan/Estudo/NanoDegree/ajna/busca/utils/histograms.pkl", "rb"))
labels = pickle.load(open("/home/ivan/Estudo/NanoDegree/ajna/busca/utils/labels.pkl", "rb"))
clf = RandomForestClassifier()
clf.fit(histograms, labels)

def hist(img):
    histo = np.histogram(img, bins=n_bins, density=True)
    return histo[0]

def vaziooucheio(file):
    cc = misc.imread(file)
    return clf.predict([hist(cc)])

def vaziooucheiodescritivo(file):
    teste = vaziooucheio(file)
    if teste[0] == 0:
        return "Contêiner avaliado como VAZIO"
    else:
        return "Contêiner avaliado como NÃO VAZIO"
