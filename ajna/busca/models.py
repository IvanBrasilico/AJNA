import os
from django.db import models
import datetime
import time
from .filefunctions import carregaarquivos
from .bsonimage import BsonImage, BsonImageList
# Create your models here.


class FonteImagem(models.Model):
    nome = models.CharField(max_length=20)
    caminho = models.CharField(max_length=200)
    pub_date = models.DateTimeField('Data do escaneamento retirada do arquivo XML')

    def __str__(self):
        return self.nome


class ConteinerEscaneado(models.Model):
    fonte = models.ForeignKey(FonteImagem, on_delete=models.CASCADE)
    numero = models.CharField(max_length=11)
    pub_date = models.DateTimeField('Data de registro')
    arqimagemoriginal = models.CharField(max_length=150, blank=True)
    arqimagem = models.CharField(max_length=150, blank=True)
    truckid = models.CharField(max_length=150, blank=True)
    codigoplano = models.BinaryField(max_length=1000, null=True)
    exportado = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['numero']),
            models.Index(fields=['pub_date']),
            models.Index(fields=['truckid']),
        ]
        unique_together = ('numero', 'pub_date')

    def __str__(self):
        return self.numero

    def getTotal():
        return ConteinerEscaneado.objects.count()

    def getTotalporFonteImagem():
        return ConteinerEscaneado.objects.values('fonte').annotate(fcount=models.Count('fonte'))


class Agendamento(models.Model):
    fonte = models.ForeignKey(FonteImagem, on_delete=models.CASCADE)
    mascarafiltro = models.CharField(
        'Mascara no formato " % Y % m % d" mais qualquer literal', max_length=20)
    diaspararepetir = models.IntegerField()
    proximocarregamento = models.DateTimeField('Data do próximo agendamento')

    class Meta:
        indexes = [
            models.Index(fields=['proximocarregamento']),
        ]

    def processamascara(self):
        return self.proximocarregamento.strftime(self.mascarafiltro)

    def agendamentos_pendentes():
        return Agendamento.objects.all().filter(proximocarregamento__lt=datetime.datetime.now())

    def agendamentos_programados():
        return Agendamento.objects.all().filter(proximocarregamento__gt=datetime.datetime.now())

    def __str__(self):
        return self.fonte.nome+' '+self.proximocarregamento.strftime('%Y%m%d %H%M')


def trata_agendamentos():
    lista_agendamentos = Agendamento.agendamentos_pendentes()
    if len(lista_agendamentos) > 0:
        print('Tem agendamentos!')
        from .views import homedir, size
        for ag in lista_agendamentos:
            fonte = ag.fonte
            caminho = ag.processamascara()
            mensagem = carregaarquivos(homedir, caminho, size, fonte)
            with open('agendamento'+ag.fonte.nome+ag.proximocarregamento.strftime('%Y%m%d %H%M'), 'w') as f:
                f.write(mensagem)
                f.close()
            ag.proximocarregamento = ag.proximocarregamento + \
                datetime.timedelta(days=ag.diaspararepetir)
            ag.save()
    else:
        print('Não tem agendamentos!')


IMG_FOLDER = os.path.join(os.path.dirname(
    __file__), 'static', 'busca')
DEST_PATH = os.path.join(os.path.dirname(__file__))
UNIDADE = 'ALFSTS:'

from django.forms.models import model_to_dict


def exporta_arquivos(batch_size):
    if not batch_size:
        batch_size = 300
    s0 = time.time()
    nao_exportados = ConteinerEscaneado.objects.all().filter(
        exportado=0)[:batch_size]
    dict_export = {}
    start = nao_exportados[0].pub_date
    end = nao_exportados[batch_size - 1].pub_date
    s1 = time.time()
    print('Consulta no banco efetuada em ', s1 - s0, ' segundos')
    for containerescaneado in nao_exportados:
        # print(containerescaneado.numero)
        imagem = os.path.join(*containerescaneado.arqimagemoriginal.split('\\'))
        dict_export[str(containerescaneado.id)] = {
            'contentType': 'image/jpeg',
            'id': UNIDADE + str(containerescaneado.id),
            'imagem': imagem,
            'dataescaneamento': containerescaneado.pub_date,
            'numeroinformado': containerescaneado.numero,
            'truckid': containerescaneado.truckid,
            'recintoid': str(containerescaneado.fonte.id),
            'recinto': containerescaneado.fonte.nome
        }
    s2 = time.time()
    print('Dicionário montado em ', s2 - s1, ' segundos')
    bsonimagelist = BsonImageList()
    for key, value in dict_export.items():
        # Puxa arquivo .jpg
        jpegfile = os.path.join(IMG_FOLDER, value['imagem'])
        print(jpegfile)
        bsonimage = BsonImage(filename=jpegfile, **value)
        bsonimagelist.addBsonImage(bsonimage)
        # Puxa arquivo .xml
        xmlfile = jpegfile.split('S_stamp')[0] + '.xml'
        value['contentType'] = 'text/xml'
        bsonimage = BsonImage(filename=xmlfile, **value)
        bsonimagelist.addBsonImage(bsonimage)
    name = datetime.datetime.strftime(start, '%Y-%m-%d_%H-%M-%S') + '_' + \
        datetime.datetime.strftime(end, '%Y-%m-%d_%H-%M-%S')
    s3 = time.time()
    print('Bson montado em ', s3 - s2, ' segundos')
    bsonimagelist.tofile(os.path.join(DEST_PATH, name + '_list.bson'))
    s4 = time.time()
    print('Bson salvo em ', s4 - s3, ' segundos')
    for containerescaneado in nao_exportados:
        containerescaneado.exportado = 1
        containerescaneado.save()
    s4 = time.time()
    print('Banco de dados atualizado em ', s4 - s3, ' segundos')
    return dict_export, name, len(nao_exportados)
