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

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^busca/', include('busca.urls')),
]


##Inicia Thread para checar agendamentos!!!
import threading
import schedule
import time

class myThread (threading.Thread):
   def __init__(self, threadID, name):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.lastrun = 0
   def run(self):
       print ("Starting " + self.name)
       schedule.every(5).minutes.do(trata_agendamentos)
       schedule.every(2).minutes.do(exporta_bson)
       while True:
           schedule.run_pending()
           time.sleep(1)
       print ("Exiting " + self.name)

thread1 = myThread(1, "Thread-Agendamentos")
thread1.start()
