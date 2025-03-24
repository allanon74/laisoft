from django.urls import path
from django.contrib.auth.decorators import login_required

#_Urls PRATICHE
from . import views

urlpatterns = [
#	path('tabella/', views.tabella_turni, name='tabella_turni'),
#	path('test/', views.tabella_turni_test, name='tabella_turni_test'),
#	path('semplice/', views.tabella_turni_semplice, name='tabella_turni_semplice'),
#	path('lista/ferie/', views.InserisciFerie, name="Inserimento Ferie"),
#	path('lista/pratica_d_ufficio/', views.PraticaUfficio, name="Pratica d'ufficio"),
#	path('lista/dettaglio/<int:id_ticket>/', views.DettaglioTicket, name="Dettaglio Ticket"),	
#	path('lista/dettaglio/', views.DettaglioTicket.as_view(), name='dettaglio_ticket'),
	path('lista/dettaglio/', login_required(views.VistaDettaglioTicket.as_view()), name="dettaglio_ticket_2"),
	path('dettaglio/', login_required(views.VistaDettaglioTicket.as_view()), name="dettaglio_ticket"),
	#path('lista/dettaglio/aggiungi_azione/', views.aggiungi_azione, name="aggiungi_azione"),
	#path('lista/dettaglio/risolvi/', views.risolvi_ticket, name="Risolvi Ticket"),
	path('inserisci/inserito/', login_required(views.inserisci_ticket), name="inserito Ticket"),
	path('inserisci/', login_required(views.form_inserisci_ticket), name="inserisci_ticket"),
#	path('dettaglio/<int:id_ticket>/', views.visualizza_ticket, name="dettaglio_ticket"),
	path('lista/', views.VistaTicket.as_view(), name='lista_ticket'),
	path('', views.VistaTicket.as_view(), name="lista_ticket_2"),
]
