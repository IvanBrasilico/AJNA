import os
from django.db import models
import datetime
import time
from .filefunctions import carregaarquivos
from .bsonimage import BsonImage, BsonImageList
# Create your models here.
from sys import platform


class FonteImagem(models.Model):
    nome = models.CharField(max_length=20)
    caminho = models.CharField(max_length=200)
    pub_date = models.DateTimeField('Data de registro')

    def __str__(self):
        return self.nome


class ConteinerEscaneado(models.Model):
    fonte = models.ForeignKey(FonteImagem, on_delete=models.CASCADE)
    numero = models.CharField(max_length=11)
    pub_date = models.DateTimeField(
        'Data do escaneamento retirada do arquivo XML')
    file_mdate = models.DateTimeField('Data da última modificação do arquivo')
    file_cdate = models.DateTimeField('Data da criação do arquivo (Windows)')
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
        with open('log' + datetime.datetime.now().strftime('%Y%m%d'), 'a') as f:
            for ag in lista_agendamentos:
                fonte = ag.fonte
                caminho = ag.processamascara()
                mensagem, erro = carregaarquivos(homedir, caminho, size, fonte)
                f.write(mensagem+'\n')
                ag.proximocarregamento = ag.proximocarregamento + \
                    datetime.timedelta(days=ag.diaspararepetir)
                ag.save()
            f.close()
    else:
        print('Não tem agendamentos!')


IMG_FOLDER = os.path.join(os.path.dirname(
    __file__), 'static', 'busca')
DEST_PATH = os.path.join(os.path.dirname(__file__))
UNIDADE = 'ALFSTS:'
BATCH_SIZE = 1000

# Uncomment if images are outside (on development station for example)
# Automatically assumes that if running on linux is on development station,
# Since this module normally run in windows stations to acquire files
# """
if platform != 'win32':
    print('Tks, Lord!!! No weird windows...')
    IMG_FOLDER = os.path.join(os.path.dirname(
        __file__), '..', '..', '..', 'imagens')
    DEST_PATH = os.path.join(os.path.dirname(
        __file__), '..', '..', '..', 'files', 'BSON')
# """


def exporta_bson(batch_size=BATCH_SIZE):
    if not batch_size:
        batch_size = BATCH_SIZE
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
        imagem = os.path.join(
            *containerescaneado.arqimagemoriginal.split('\\'))
        dict_export[str(containerescaneado.id)] = {
            'contentType': 'image/jpeg',
            'id': UNIDADE + str(containerescaneado.id),
            'UNIDADE': UNIDADE,
            'idcov': str(containerescaneado.id),
            'imagem': imagem,
            'dataescaneamento': containerescaneado.pub_date,
            'criacaoarquivo': containerescaneado.file_cdate,
            'modificacaoarquivo': containerescaneado.file_mdate,
            'numeroinformado': containerescaneado.numero,
            'truckid': containerescaneado.truckid,
            'recintoid': str(containerescaneado.fonte.id),
            'recinto': containerescaneado.fonte.nome
        }
    s2 = time.time()
    print('Dicionário montado em ', s2 - s1, ' segundos')
    with open('log' + datetime.datetime.now().strftime('%Y%m%d'), 'a') as f:
        bsonimagelist = BsonImageList()
        for key, value in dict_export.items():
            # Puxa arquivo .jpg
            jpegfile = os.path.join(IMG_FOLDER, value['imagem'])
            # print(jpegfile)
            try:
                bsonimage = BsonImage(filename=jpegfile, **value)
                bsonimagelist.addBsonImage(bsonimage)
            except FileNotFoundError as err:
                f.write(str(err)+'\n')
                print(str(err))
                print(value['imagem'])

            # Puxa arquivo .xml
            try:
                xmlfile = jpegfile.split('S_stamp')[0] + '.xml'
                value['contentType'] = 'text/xml'
                bsonimage = BsonImage(filename=xmlfile, **value)
                bsonimagelist.addBsonImage(bsonimage)
            except FileNotFoundError as err:
                f.write(str(err)+'\n')
                print(str(err))
                print(value['imagem'])
        f.close()
    name = datetime.datetime.strftime(start, '%Y-%m-%d_%H-%M-%S') + '_' + \
        datetime.datetime.strftime(end, '%Y-%m-%d_%H-%M-%S')
    s3 = time.time()
    print('Bson montado em ', s3 - s2, ' segundos')
    for containerescaneado in nao_exportados:
        containerescaneado.exportado = 1
        containerescaneado.save()
    s4 = time.time()
    print('Banco de dados atualizado em ', s4 - s3, ' segundos')
    bsonimagelist.tofile(os.path.join(DEST_PATH, name + '_list.bson'))
    s5 = time.time()
    print('Bson salvo em ', s5 - s4, ' segundos')
    return dict_export, name, len(nao_exportados)
