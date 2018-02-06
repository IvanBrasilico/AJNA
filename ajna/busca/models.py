from django.db import models
import datetime
from .filefunctions import carregaarquivos
# Create your models here.

class FonteImagem(models.Model):
    nome = models.CharField(max_length=20)
    caminho = models.CharField(max_length=200)
    pub_date = models.DateTimeField('Data de registro')
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
    login = models.CharField(max_length=50, blank=True)
    alerta = models.CharField(max_length=2, blank=True)
    class Meta:
        indexes = [
            models.Index(fields=['numero']),
            models.Index(fields=['pub_date']),
            models.Index(fields=['truckid']),
            models.Index(fields=['login']),
            models.Index(fields=['alerta']),
        ]
        unique_together = ("numero", "pub_date")
    def __str__(self):
        return self.numero
    def getTotal():
        return ConteinerEscaneado.objects.count()
    def getTotalporFonteImagem():
        return ConteinerEscaneado.objects.values('fonte').annotate(fcount=models.Count('fonte'))


class Agendamento(models.Model):
    fonte = models.ForeignKey(FonteImagem, on_delete=models.CASCADE)
    mascarafiltro = models.CharField('Mascara no formato "%Y%m%d" mais qualquer literal', max_length=20) #
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
        return self.fonte.nome+' '+self.proximocarregamento.strftime("%Y%m%d %H%M")

def trata_agendamentos():
       lista_agendamentos = Agendamento.agendamentos_pendentes()
       if len(lista_agendamentos) > 0:
           print("Tem agendamentos!")
           from .views import homedir, size
           for ag in lista_agendamentos:
               fonte = ag.fonte
               caminho = ag.processamascara()
               mensagem = carregaarquivos(homedir, caminho, size, fonte)
               with open('agendamento'+ag.fonte.nome+ag.proximocarregamento.strftime("%Y%m%d %H%M"), 'w') as f:
                   f.write(mensagem)
                   f.close()
               ag.proximocarregamento = ag.proximocarregamento + datetime.timedelta(days=ag.diaspararepetir)
               ag.save()
       else:
           print("Não tem agendamentos!")
           

    


