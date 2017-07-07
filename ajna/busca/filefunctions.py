from PIL import Image
import numpy as np
import os
import glob
from scipy import misc


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
        destdir = os.path.dirname(ofile)
        destfile = destdir+'tmp_'+filename
        print("**"+destfile)
        misc.imsave(destfile, imcortada)
        im = Image.load(destfile)
        imnova = im.resize(size)
        imnova.save(odest, quality=100)
        os.remove(destfile)
        return imnova

def carregaarquivos(path):
    return ""


