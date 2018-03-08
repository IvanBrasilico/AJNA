# -*- coding: utf-8 -*-


from django.conf.urls import url

from django.conf import settings
from django.conf.urls.static import static


from . import views

app_name = 'busca'

urlpatterns = [
    url(r'^$', views.indexview, name='index'),
    # ex: /busca/5/
    url(r'^(?P<pk>[0-9]+)/$', views.FonteDetailView.as_view(), name='FonteDetailView'),
    url(r'^conteiner/(?P<pk>[0-9]+)/$', views.conteinerdetail, name='c'),
    # ex: /busca/5/results/
    # url(r'^(?P<question_id>[0-9]+)/results/$', views.results, name='results'),
    # ex: /busca/formimagem
    # url(r'^frmimagem/$', views.frmimagem, name='frmimagem'),
    url(r'^buscaimagem/$', views.buscaimagem, name='buscaimagem'),
    url(r'^buscaconteiner/$', views.buscaconteiner, name='buscaconteiner'),    
    url(r'^trataagendamentos/$', views.trataagendamentos, name='trataagendamentos'),
    url(r'^exportabson/$', views.exportabson, name='exportabson'),
    url(r'^zerabson/$', views.zerabson, name='zerabson'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

