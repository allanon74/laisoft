# -*- coding: utf-8 -*-
from django.urls import path
#from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
	#path('test/', views.test, name='test'),
	#path('completo/', views.completo, name='completo'),
	#path('suggerimento/', views.suggerimento, name='suggerimento'),
	#path('pdf/', views.pdf, name='pdf'),
	#path('pdfmanual/', views.pdfManual, name='pdfmanual'),
	#path('', views.index, name='index'),
	#path('stampa_valutazione/<int:id>/', views.stampa_valutazione, name='stampa_valutazione'),
	#path('stampa_griglia/', views.stampa_griglia, name='stampa_griglia'),
	#path('prova/', views.Stampa.as_view(), name='stampa_prova'),
	path('stampadesignazione/<int:id>/', views.StampaDesignazione.as_view(), name='stampa_designazone'),
	path('stampapassword/<int:id>/', views.StampaPassword.as_view(), name='stampa_password'),
	path('stampaambito/<int:id>/', views.StampaAmbito.as_view(), name='stampa_ambito'),
	path('stampaautorizzazione/<int:id>/', views.StampaAutorizzazione.as_view(), name='stampa_autorizzazione'),
]