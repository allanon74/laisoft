from django.contrib.auth.decorators import login_required

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TemaViewSet, VistaViewSet, MansioneViewSet, MansioneTranslationViewSet,
    AttivitaViewSet, AttivitaTranslationViewSet, PrioritaViewSet, PrioritaTranslationViewSet,
    AnnoViewSet, SquadraViewSet, SquadraTranslationViewSet, TipologiaViewSet,
    TipologiaTranslationViewSet, CollaboratoreViewSet, CdCViewSet, CdCTranslationViewSet,
    StrutturaViewSet, StrutturaTranslationViewSet, DirittoViewSet, EventoViewSet,
    TagViewSet, EventoTranslationViewSet, InterventoViewSet,
    TeamViewSet, FotoViewSet, LavoroViewSet, TempiLavoroViewSet, AllegatoViewSet,
    AnnotazioneViewSet, EventoSegnalazioneViewSet, CollaboratoreMansioneViewSet,
    CollaboratoreAssenzaViewSet, CollaboratoreReperibilitaViewSet, UserViewSet,
    SegnalazioneViewSet, SegnalazioneCompletaViewSet, SegnalazioneStoricaViewSet, SegnalazioneStoricaCompletaViewSet, 
    AuthTokenViewSet,
)

#	2025_06_12_Router for REST API 

router = DefaultRouter()
router.register(r'temi', TemaViewSet)
router.register(r'viste', VistaViewSet)
router.register(r'mansioni', MansioneViewSet)
router.register(r'mansioni-translation', MansioneTranslationViewSet)
router.register(r'attivita', AttivitaViewSet)
router.register(r'attivita-translation', AttivitaTranslationViewSet)
router.register(r'priorita', PrioritaViewSet)
router.register(r'priorita-translation', PrioritaTranslationViewSet)
router.register(r'anni', AnnoViewSet)
router.register(r'squadre', SquadraViewSet)
router.register(r'squadre-translation', SquadraTranslationViewSet)
router.register(r'tipologie', TipologiaViewSet)
router.register(r'tipologie-translation', TipologiaTranslationViewSet)
router.register(r'collaboratori', CollaboratoreViewSet)
router.register(r'cdc', CdCViewSet)
router.register(r'cdc-translation', CdCTranslationViewSet)
router.register(r'strutture', StrutturaViewSet)
router.register(r'strutture-translation', StrutturaTranslationViewSet)
router.register(r'diritti', DirittoViewSet)
router.register(r'eventi', EventoViewSet)
router.register(r'tags', TagViewSet)
router.register(r'eventi-translation', EventoTranslationViewSet)

router.register(r'segnalazioni', SegnalazioneViewSet, basename='segnalazioni')
router.register(r'segnalazioni_complete', SegnalazioneCompletaViewSet, basename='segnalazioni_complete')
router.register(r'segnalazioni_storiche', SegnalazioneStoricaViewSet, basename='segnalazioni_storiche')
router.register(r'segnalazioni_storiche_complete', SegnalazioneStoricaCompletaViewSet, basename='segnalazioni_storiche_complete')

router.register(r'interventi', InterventoViewSet)
router.register(r'team', TeamViewSet)
router.register(r'foto', FotoViewSet)
router.register(r'lavori', LavoroViewSet)
router.register(r'tempilavoro', TempiLavoroViewSet)
router.register(r'allegati', AllegatoViewSet)
router.register(r'annotazioni', AnnotazioneViewSet)
router.register(r'evento-segnalazione', EventoSegnalazioneViewSet)
router.register(r'collaboratore-mansione', CollaboratoreMansioneViewSet)
router.register(r'collaboratore-assenza', CollaboratoreAssenzaViewSet)
router.register(r'collaboratore-reperibilita', CollaboratoreReperibilitaViewSet)
router.register(r'utenti', UserViewSet)


auth_token = AuthTokenViewSet.as_view({'post': 'create'})

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
    path('api/', include(router.urls)), # 2025-06-12 API routes for REST fW
	path('api-auth/', include('rest_framework.urls', namespace='rest_framework')), # 2025-06-12 API authentication routes
 	path('api/token/', auth_token, name='api-token'),
	]
