from django.db import models
from datetime import datetime
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
    class Meta:
        indexes = [
            models.Index(fields=['numero']),
            models.Index(fields=['pub_date']),
            models.Index(fields=['truckid']),
        ]
        unique_together = ("numero", "pub_date")
    
    def __str__(self):
        return self.numero

class Agendamento(models.Model):
    fonte = models.ForeignKey(FonteImagem, on_delete=models.CASCADE)
    mascarafiltro = models.CharField(max_length=20)
    diaspararepetir = models.IntegerField()
    proximocarregamento = models.DateTimeField('Data do próximo agendamento')
    class Meta:
        indexes = [
            models.Index(fields=['proximocarregamento']),
        ]
    def agendamentos_pendentes():
        return Agendamento.objects.all().filter(proximocarregamento__lt=datetime.now())
    def __str__(self):
        return self.fonte.nome

def trata_agendamentos():
       lista_agendamentos = Agendamento.agendamentos_pendentes()
       if len(lista_agendamentos) > 0:
           print("Tem agendamentos!")
           #processa_agendamentos(lista_agendamentos)
       else:
           print("Não tem agendamentos!")
    


