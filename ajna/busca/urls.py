# -*- coding: utf-8 -*-


from django.conf.urls import url

from django.conf import settings
from django.conf.urls.static import static


from . import views

app_name = 'busca'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    # ex: /busca/5/
    url(r'^(?P<pk>[0-9]+)/$', views.FonteDetailView.as_view(), name='FonteDetailView'),
    url(r'^conteiner/(?P<pk>[0-9]+)/$', views.conteinerdetail, name='c'),
    # ex: /busca/5/results/
    #url(r'^(?P<question_id>[0-9]+)/results/$', views.results, name='results'),
    # ex: /busca/formimagem
    url(r'^frmimagem/$', views.frmimagem, name='frmimagem'),
    url(r'^frmlistavazios/$', views.frmlistavazios, name='frmlistavazios'),
    url(r'^frmcomparapesos/$', views.frmcomparapesos, name='frmcomparapesos'),
    url(r'^listavazios/$', views.listavazios, name='listavazios'),
    url(r'^comparapesos/$', views.comparapesos, name='comparapesos'),
    url(r'^buscaimagem/$', views.buscaimagem, name='buscaimagem'),
    url(r'^buscaconteiner/$', views.buscaconteiner, name='buscaconteiner'),    
    url(r'^buscasimilar/(?P<pk>[0-9]+)/$', views.buscasimilar, name='buscasimilar'),
    url(r'^indexar/$', views.indexar, name='indexar'),
    url(r'^carregaimagens/$', views.carregaimagens, name='carregaimagens'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

