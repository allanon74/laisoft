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
#	path('lista/dettaglio/', login_required(views.visualizza_ticket), name="dettaglio_ticket_2"),
#	path('dettaglio/', login_required(views.visualizza_ticket), name="dettaglio_ticket"),
#	#path('lista/dettaglio/aggiungi_azione/', views.aggiungi_azione, name="aggiungi_azione"),
#	#path('lista/dettaglio/risolvi/', views.risolvi_ticket, name="Risolvi Ticket"),
#	path('inserisci/inserito/', login_required(views.inserisci_ticket), name="inserito Ticket"),
#	path('inserisci/', login_required(views.form_inserisci_ticket), name="inserisci_ticket"),
#	path('dettaglio/<int:id_ticket>/', views.visualizza_ticket, name="dettaglio_ticket"),
#	path('lista/', views.VistaTicket.as_view(), name='lista_ticket'),
#	path('', login_required(views.main_menu), name='main'),
	path('', login_required(views.carica_vista), name='gic_main'),
	path('full/', views.VistaMain.as_view(), name='gic_full'),
	path('segnalazioni/', login_required(views.VistaSegnalazioni.as_view()), name='gic_segnalazioni'),
	path('segnalazione/', login_required(views.VistaSegnalazione.as_view()), name='gic_segnalazione'),
	path('intervento/', login_required(views.VistaIntervento.as_view()), name='gic_intervento'),
	path('interventi/', login_required(views.VistaInterventi.as_view()), name='gic_interventi'),
	path('operai/', login_required(views.VistaOperai.as_view()), name='gic_operai'),
	path('operailavoro/', login_required(views.VistaOperaiLavoro.as_view()), name='gic_operai_lavoro'),
	path('collaboratori/', login_required(views.VistaCollaboratori.as_view()), name='gic_collaboratori'),
	path('lavori_verifica/', login_required(views.VistaLavoriVerifica.as_view()), name='gic_lavori_verifica'),
	path('report/', login_required(views.VistaReport.as_view()), name='gic_report'),
	path('report/csv/<str:dt_da>/<str:dt_a>/', login_required(views.ReportCSVDt), name='gic_report_csv_dt'),
	path('report/csv/', login_required(views.ReportCSV), name='gic_report_csv'),
	path('jq/', views.VistaJq.as_view(), name='jq'),
	path('segnalazionestruttura/', views.VistaStrutture.as_view(), name="gic_segnalazioni_strutture"),
	]
