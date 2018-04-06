"""ajna URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from busca.models import trata_agendamentos, exporta_bson
from busca.conta_xmls_originais import conta_por_agendamento

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^busca/', include('busca.urls')),
]


# Inicia Thread para checar agendamentos!!!
import threading
import schedule
import time


def trata_agendamentos_exporta_bson():
    """Para não ter concorrência entre Threads,
    somente esta fará save no banco, e sempre sequencial!!!
    """
    import http.client
    conn = http.client.HTTPConnection('localhost:8000')
    conn.request('GET', '/busca/trataagendamentos/')
    r = conn.getresponse()
    r.read()
    print(r.status)
    time.sleep(10)
    conn = http.client.HTTPConnection('localhost:8000')
    conn.request('GET', '/busca/exportabson/')
    r = conn.getresponse()
    r.read()
    print(r.status)


class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.lastrun = 0

    def run(self):
        print("Starting " + self.name)
        conta_por_agendamento()
        schedule.every(1).minutes.do(trata_agendamentos_exporta_bson)
        while True:
            schedule.run_pending()
            time.sleep(1)
        print("Exiting " + self.name)


thread1 = myThread(1, "Thread-Agendamentos")
thread1.start()
