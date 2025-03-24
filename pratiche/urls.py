from django.urls import path

#_Urls PRATICHE
from . import views

urlpatterns = [
#	path('tabella/', views.tabella_turni, name='tabella_turni'),
#	path('test/', views.tabella_turni_test, name='tabella_turni_test'),
#	path('semplice/', views.tabella_turni_semplice, name='tabella_turni_semplice'),
	path('lista/ferie/', views.InserisciFerie, name="Inserimento Ferie"),
	path('lista/pratica_d_ufficio/', views.PraticaUfficio, name="Pratica d'ufficio"),
	path('lista/completato/<int:id_delega>/', views.CompletaPratica, name="Completa Pratica"),	
	path('lista/', views.VistaTecnici.as_view(), name='lista_pratiche'),
]
