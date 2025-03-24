from django.urls import path
from django.contrib.auth.decorators import login_required

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
	path('stampaformulario/<int:id>/', views.StampaFormulario.as_view(), name='stampa_valutazione'),
	path('stampaformularioted/<int:id>/', views.StampaFormularioDt.as_view(), name='stampa_valutazione_tedesco'),
	path('lista/dettaglio/', login_required(views.DettaglioFormulario), name='dettaglio_formulario'),
	path('lista/', views.VistaGriglia.as_view(), name='lista_formulari'), 
#	path('test/', login_required(views.Formulari), name ="test_formulari"),
]
