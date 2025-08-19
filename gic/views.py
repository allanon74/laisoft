from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import modelformset_factory
from django.utils import timezone
from django.db.models import F, Q
from django.urls import reverse_lazy
from django.http import StreamingHttpResponse, HttpResponse
import humanize
from django_filters.rest_framework import DjangoFilterBackend


from django.contrib.auth import authenticate


from rest_framework import viewsets, status, permissions

from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from rest_framework.authtoken.admin import User
from rest_framework.authentication import TokenAuthentication


from .models import (
    Tema, Vista, Mansione, MansioneTranslation, Attivita, AttivitaTranslation,
    Priorita, PrioritaTranslation, Anno, Squadra, SquadraTranslation, Tipologia,
    TipologiaTranslation, Collaboratore, CdC, CdCTranslation, Struttura, StrutturaTranslation,
    Diritto, Evento, Tag, EventoTranslation, Segnalazione, Intervento, Team,
    Foto, Lavoro, TempiLavoro, Allegato, Annotazione, EventoSegnalazione,
    CollaboratoreMansione, CollaboratoreAssenza, CollaboratoreReperibilita
)
from .serializers import (
    TemaSerializer, VistaSerializer, MansioneSerializer, MansioneTranslationSerializer,
    AttivitaSerializer, AttivitaTranslationSerializer, PrioritaSerializer, PrioritaTranslationSerializer,
    AnnoSerializer, SquadraSerializer, SquadraTranslationSerializer, TipologiaSerializer,
    TipologiaTranslationSerializer, CollaboratoreSerializer, CdCSerializer, CdCTranslationSerializer,
    StrutturaSerializer, StrutturaTranslationSerializer, DirittoSerializer, EventoSerializer,
    TagSerializer, EventoTranslationSerializer, SegnalazioneSerializer, InterventoSerializer,
    TeamSerializer, FotoSerializer, LavoroSerializer, TempiLavoroSerializer, AllegatoSerializer,
    AnnotazioneSerializer, EventoSegnalazioneSerializer, CollaboratoreMansioneSerializer,
    CollaboratoreAssenzaSerializer, CollaboratoreReperibilitaSerializer, UserSerializer,
    SegnalazioneCompletaSerializer, AuthTokenSerializer,
)

import csv

from .templatetags.customform import form

import gic.models


import datetime
from datetime import timedelta

import requests
from django.shortcuts import redirect

from dipendenti.models import Dipendente, Logo
from dipendenti.views import base_context

from laisoft.settings import BASE_URL

# from .models import Tema, Segnalazione, Diritto, Intervento, Team, Collaboratore, Tipologia, TempiLavoro, Foto, Allegato, Struttura
# from .models import Lavoro, Attivita, Priorita 
from .forms import SegnalazioneFormset, SegnalazioneForm, InterventoForm, TeamForm, LavoroForm, FotoForm, AllegatoForm, SegnalazioneStrutturaForm

CAPOCANTIERE = 'capocantiere' 
CAPOSQUADRA = 'caposquadra'
COORDINATORE = 'coordinatore'
OPERAIO = 'operaio'
STRUTTURA = 'struttura'
UFFICIO = 'ufficio'

START = "start"
SAVE = "save"
NEW = "new"
AVVIA = "avvia"
TERMINA = "termina"
PAUSA = "pausa"
ERROR = "err"
ALLEGATO = "allegato"
VERIFICATO = "verificato"

"""

Il rendering delle pagine vuole un context pageconfig con i seguenti valori:
	lavori: se vuoi o non vuoi visualizzare la scheda valori 
	lavori_new: se vuoi o non vuoi visualizzare la scheda nuovo lavoro
	teams
	teams_new
	interventi
	interventi_new
	segnalazioni
	segnalazioni_new
	allegati
	annotazioni
	foto
	tempilavoro


"""

LAVORI = "lavori"
LAVORI_NEW = "lavori_new"
TEAMS = "teams"
TEAMS_NEW = "teams_new"
INTERVENTI = "interventi"
INTERVENTI_NEW = "interventi_new"
SEGNALAZIONI = "segnalazioni"
SEGNALAZIONI_NEW = "segnalazioni_new"
ALLEGATI = "allegati"
ANNOTAZIONI = "annotazioni"
FOTO = "foto"
TEMPILAVORO = "tempilavoro"
ACCESSORIO = "accessorio"
URGENTE = "urgente"
VERIFICA = "verifica"

gic_render = {}
gic_render[LAVORI] = True
gic_render[LAVORI_NEW] = True
gic_render[TEAMS] = True
gic_render[TEAMS_NEW] = True
gic_render[INTERVENTI] = True
gic_render[INTERVENTI_NEW] = True
gic_render[SEGNALAZIONI] = True
gic_render[SEGNALAZIONI_NEW] = True
gic_render[ALLEGATI] = True
gic_render[ANNOTAZIONI] = True
gic_render[FOTO] = True
gic_render[TEMPILAVORO] = True
gic_render[VERIFICA] = False

gic_render_v = {}
gic_render_v[LAVORI] = True
gic_render_v[LAVORI_NEW] = False
gic_render_v[TEAMS] = True
gic_render_v[TEAMS_NEW] = True
gic_render_v[INTERVENTI] = True
gic_render_v[INTERVENTI_NEW] = True
gic_render_v[SEGNALAZIONI] = True
gic_render_v[SEGNALAZIONI_NEW] = True
gic_render_v[ALLEGATI] = True
gic_render_v[ANNOTAZIONI] = True
gic_render_v[FOTO] = True
gic_render_v[TEMPILAVORO] = True
gic_render_v[VERIFICA] = True

gic_no_render = {}
gic_no_render[LAVORI] = False
gic_no_render[LAVORI_NEW] = True
gic_no_render[TEAMS] = False
gic_no_render[TEAMS_NEW] = True
gic_no_render[INTERVENTI] = False
gic_no_render[INTERVENTI_NEW] = True
gic_no_render[SEGNALAZIONI] = False
gic_no_render[SEGNALAZIONI_NEW] = True
gic_no_render[ALLEGATI] = False
gic_no_render[ANNOTAZIONI] = False
gic_no_render[FOTO] = False
gic_no_render[TEMPILAVORO] = False
gic_no_render[VERIFICA] = False

coll_render = {}
coll_render[LAVORI] = True
coll_render[LAVORI_NEW] = False
coll_render[TEAMS] = True
coll_render[TEAMS_NEW] = True
coll_render[INTERVENTI] = True
coll_render[INTERVENTI_NEW] = True
coll_render[SEGNALAZIONI] = True
coll_render[SEGNALAZIONI_NEW] = True
coll_render[ALLEGATI] = True
coll_render[ANNOTAZIONI] = True
coll_render[FOTO] = True
coll_render[TEMPILAVORO] = True 
coll_render[VERIFICA] = False

str_render = {}
str_render[LAVORI] = False
str_render[LAVORI_NEW] = False
str_render[TEAMS] = False
str_render[TEAMS_NEW] = False
str_render[INTERVENTI] = True
str_render[INTERVENTI_NEW] = False
str_render[SEGNALAZIONI] = True
str_render[SEGNALAZIONI_NEW] = False
str_render[ALLEGATI] = False
str_render[ANNOTAZIONI] = False
str_render[FOTO] = False
str_render[TEMPILAVORO] = False 
str_render[VERIFICA] = False


class Echo:
	def write(self, value):
		return value


def last_day_of_month(date):
	next_month = date.replace(day=28) + timedelta(days=4)
	return next_month - timedelta(days=next_month.day)

class Vista_a(LoginRequiredMixin, TemplateView):
	loggeduser = None
	dipendente = None
	admin = False
	context = {}
	login_url = reverse_lazy('users:login')
	
	def setup(self, request, *args, **kwargs):
		super().setup(request, *args, **kwargs)
		self.context = carica_diritti(base_context(request, super().get_context_data()))
		self.context['gic_render'] = gic_render
		self.loggeduser = self.context['loggeduser']
		self.dipendente = self.context['dipendente']
		self.admin = self.context['admin']
	
	class Meta:
		abstract = True

def carica_diritti(context):
	loggeduser = context['loggeduser']
	ruolo = {}
	ruolo[CAPOCANTIERE] = context['capocantiere'] = loggeduser.groups.filter(name = 'LS_GIC_capocantiere').exists()
	ruolo[CAPOSQUADRA] = context['caposquadra'] = loggeduser.groups.filter(name = 'LS_GIC_caposquadra').exists()
	ruolo[OPERAIO] = context['operaio'] = loggeduser.groups.filter(name = 'LS_GIC_operaio').exists()
	ruolo[COORDINATORE] = context['coordinatore'] = loggeduser.groups.filter(name = 'LS_GIC_coordinatore').exists()
	ruolo[STRUTTURA] = context['struttura'] = loggeduser.groups.filter(name = 'LS_GIC_struttura').exists()
	ruolo[UFFICIO] = context['ufficio'] = loggeduser.groups.filter(name = 'LS_GIC_ufficio').exists()
	
	diritto = Diritto.dict_diritti(context['dipendente'].collaboratore)
	
	context["diritto"] = diritto
	context['ruolo'] = ruolo
	context ['base_url'] = BASE_URL
	return context


# override di Lavoro per inserire il riferimento al form di Foto

#class V_Lavoro(Lavoro):
#	
#	@property 
#	def fotoform(self):
#		return FotoForm()
	

# Create your views here.
def main_menu(request):
	
	templ = "gic_start.html"
	
	context=carica_diritti(base_context(request))
	
	return render(request, templ, context)


def carica_vista(request):
	context = base_context(request)
	view = context['dipendente'].collaboratore.vista.nome_modello
	#mdl = getattr(gic.views, view)
	#redirect(mdl.as_view())
	#return mdl
	return redirect(view)


class VistaMain(Vista_a):
	template_name = "gic_start.html"

	action = START
	
# 	coll_render = {}
# 	for key, value in gic_render.items():
# 		coll_render[key] = value
# 		
# 	coll_render['lavori_new'] = False
	
	def post(self, request, *args, **kwargs):
		mdl = None
		frm = None
		
		m = request.POST.get('model')
		
		if m:
			mdl = getattr(gic.models, m)
			frm = type(form(mdl()))
			self.action = request.POST.get('action', START)
			
			if self.action == SAVE:
				inst = mdl.objects.get(pk=request.POST.get('id'))
				f = frm(request.POST, instance = inst)
				if f.is_valid():
					f.save()
				self.action = START
				request.POST={}
			
			elif self.action == NEW:
# 				f = frm(request.POST)
# #				frm.fields['stato'].required = False
# 				n_seg = f.save()
# 				self.action = START
# 				request.POST= {}

				
				f = frm(request.POST)
				if f.is_valid():
					n_seg = f.save()
					self.action = START
					request.POST = {}
				else:
					print(f.errors)

			
			elif self.action == ALLEGATO:
				sg = Segnalazione.objects.get(id=request.POST["id_segnalazione"])
				alg = Allegato(
					descrizione = request.POST['descrizione'],
					segnalazione = sg,
					file = request.FILES["file"],
					)
				alg.save()
				request.POST={}
    
			elif self.action == VERIFICATO:
				inst = mdl.objects.get(pk=request.POST.get('id'))
				inst.stato = Tipologia.tipologia("TO", "VER")
				inst.caposquadra = self.dipendente.collaboratore
				inst.save()
				self.action = START
				request.POST={}
				
				
		return render(request, self.template_name, self.get_context_data(self, *args, **kwargs))

	def get_context_data(self, *args, **kwargs):
		
		ruolo = self.context['ruolo']
# 		interv = None
# 		segn = None
# 		if not (ruolo[CAPOCANTIERE] or ruolo[UFFICIO] or ruolo[COORDINATORE]):
# 			if ruolo[CAPOSQUADRA]:
# 				interv = self.dipendente.collaboratore.squadra.interventi()
# 				segn = Segnalazione.objects.exclude(stato__abbreviazione="VER") # INSERITE tutte le segnalazioni per un bug: da RISOLVERE
# 			elif ruolo[STRUTTURA]:
# 				segn = Segnalazione.objects.exclude(stato__abbreviazione="VER").filter(struttura__in = self.dipendente.collaboratore.struttura_set.all())
# 		else:
# 			interv = Intervento.objects.exclude(stato__abbreviazione="VER")
# 			segn = Segnalazione.objects.exclude(stato__abbreviazione="VER")
	
# 		interv = interv.order_by("stato__ordine","-priorita__valore","-data_creazione")
# 		segn = segn.order_by("stato__ordine","-data_creazione").exclude(data_pianificazione__gt = timezone.now())
		
# 		self.context['interventi'] = interv
# 		self.context['segnalazioni'] = segn
# 		self.context['action'] = self.action
# #		self.context['seg_v'] = Segnalazione.objects.filter(stato__abbreviazione="VER").order_by("-data_creazione")
# 		self.context['oggi'] = timezone.now()
		
# 		self.context['collaboratori'] = Collaboratore.objects.all().order_by('dipendente__cognome', 'dipendente__nome')
# 		self.context['segnalazione_new'] = SegnalazioneForm 
# 		self.context["intervento_new"] = InterventoForm
# 		self.context["team_new"] = TeamForm
# 		self.context['lavoro_new'] = LavoroForm
# 		self.context['coll_render'] = coll_render
		
# 		self.context['gic_render'] = gic_no_render

# prova ottimizzata

		oggi = timezone.now()

		# QuerySet base per Segnalazioni e Interventi
		segnalazioni_qs = Segnalazione.objects.select_related(
			'struttura', 'tipo', 'stato'
		).prefetch_related(
			'tags', 'eventi'
		).exclude(
			stato__abbreviazione="VER"
		).filter(
			data_pianificazione__lte=oggi
		).order_by("stato__ordine", "-data_creazione")

		interventi_qs = Intervento.objects.select_related(
			'struttura', 'priorita', 'preposto', 'stato'
		).exclude(
			stato__abbreviazione="VER"
		).order_by("stato__ordine", "-priorita__valore", "-data_creazione")

		# Filtri per ruolo
		if not (ruolo[CAPOCANTIERE] or ruolo[UFFICIO] or ruolo[COORDINATORE]):
			if ruolo[CAPOSQUADRA]:
				interventi_qs = self.dipendente.collaboratore.squadra.interventi()
				segnalazioni_qs = segnalazioni_qs
			elif ruolo[STRUTTURA]:
				strutture = self.dipendente.collaboratore.struttura_set.all()
				segnalazioni_qs = segnalazioni_qs.filter(struttura__in=strutture)
				interventi_qs = Intervento.objects.none()
			else:
				interventi_qs = Intervento.objects.none()
				segnalazioni_qs = Segnalazione.objects.none()

		# Assegnazione al context
		self.context.update({
			'interventi': interventi_qs,
			'segnalazioni': segnalazioni_qs,
			'oggi': oggi,
			'action': self.action,
			'collaboratori': Collaboratore.objects.select_related('dipendente').order_by('dipendente__cognome', 'dipendente__nome'),
			'segnalazione_new': SegnalazioneForm,
			'intervento_new': InterventoForm,
			'team_new': TeamForm,
			'lavoro_new': LavoroForm,
			'coll_render': coll_render,
			'gic_render': gic_no_render,
		})
		
		return self.context
	

class VistaSegnalazioni(VistaMain):
	template_name = "gic_segnalazioni.html"
		
	def get_context_data(self, *args, **kwargs):
		self.context = super().get_context_data(*args, **kwargs)
		self.context['gic_render'] = gic_no_render
		return self.context

class VistaInterventi(VistaMain):
	template_name = "gic_interventi.html"

	def get_context_data(self, *args, **kwargs):
		self.context = super().get_context_data(*args, **kwargs)
		self.context['gic_render'] = gic_no_render
		return self.context

class VistaCollaboratori(VistaMain):
	template_name = "gic_collaboratori.html"
	login_url = "/login/"

	def get_context_data(self, **kwargs):
		context = base_context(self.request)
		context['collaboratori'] = Collaboratore.objects.select_related('dipendente').order_by(
			'dipendente__cognome', 'dipendente__nome'
		)
		context['gic_render'] = gic_render
		return context

class VistaJq(VistaMain):
	template_name = "gic_jquery.html"
	
	def get_context_data(self, *args, **kwargs):
		self.context = super().get_context_data(*args, **kwargs)
		self.context['gic_render'] = gic_render
		return self.context
	
class VistaLavoriVerifica(VistaMain):
	template_name = "gic_lavori.html" 

	def get_context_data(self, *args, **kwargs):
     
		# self.context = super().get_context_data(*args, **kwargs)
		# self.context['gic_render'] = gic_render_v
		# self.context['lavori'] = Lavoro.objects.filter(stato = Tipologia.tipologia('TO', 'CHI')).order_by("-data_modifica")
		# self.context['foto_form'] = FotoForm
  
		
		oggi = timezone.now()

		# Recupera lo stato "CHI" (chiuso) una sola volta
		stato_chiuso = Tipologia.tipologia('TO', 'CHI')

		# Ottimizza la query dei lavori chiusi con select_related per evitare query nidificate
		lavori_qs = Lavoro.objects.select_related(
			'collaboratore__dipendente',
			'team__attivita',
			'team__intervento__segnalazione',
			'team__intervento__struttura',
			'team__intervento__priorita',
			'stato'
		).filter(
			stato=stato_chiuso
		).order_by('-data_modifica')

		self.context.update({
			'gic_render': gic_render_v,
			'lavori': lavori_qs,
			'foto_form': FotoForm,
		})

		
		return self.context 

"""
class VistaIntervento(Vista_a):
	template_name = "gic_intervento.html"
	action = ERROR
	id_int = ERROR
	
	def get(self, request, *args, **kwargs):
		self.id_int = request.GET.get("id", ERROR)
		if self.id_int == ERROR:
			redirect(VistaInterventi)
		return render(request, self.template_name, self.get_context_data(self, *args, **kwargs))
	
	def post(self, request, *args, **kwargs):
		self.action = request.POST.get('action', ERROR)
		m = request.POST.get('model')
		self.id_int = request.POST.get("id", ERROR)
		if self.id_int == ERROR:
			self.id_int = request.GET.get("id", ERROR)
		if self.id_int == ERROR:
			redirect(VistaInterventi)
		if m:
			mdl = getattr(gic.models, m)
			frm = type(form(mdl()))
			
		if self.action == ERROR:
			redirect(VistaInterventi)
		elif self.action == SAVE:
			inst = mdl.objects.get(pk=request.POST.get('id'))
			f = frm(request.POST, instance = inst)
			if f.is_valid():
				f.save()
			self.action = START
		elif self.action == NEW:
				f = frm(request.POST)
#				frm.fields['stato'].required = False
				n_seg = f.save()
				self.action = START
				request.POST= {}
		return render(request, self.template_name, self.get_context_data(self, *args, **kwargs))

	def get_context_data(self, *args, **kwargs):
		
		intervento = Intervento.objects.get(id=self.id_int)
		
		

		self.context['intervento'] = intervento
		self.context['action'] = self.action
		self.context['oggi'] = datetime.now()
		
		self.context["intervento_new"] = InterventoForm
		self.context["team_new"] = TeamForm
		self.context['lavoro_new'] = LavoroForm
		self.context['gic_render'] = gic_render
		
		return self.context

class VistaSegnalazione(Vista_a):
	template_name = "gic_segnalazione.html"
	action = ERROR
	id_seg = ERROR
	
	def get(self, request, *args, **kwargs):
		self.id_seg = request.GET.get("id", ERROR)
		if self.id_seg == ERROR:
			redirect(VistaSegnalazioni)
		return render(request, self.template_name, self.get_context_data(self, *args, **kwargs))
	
	def post(self, request, *args, **kwargs):
		self.action = request.POST.get('action', ERROR)
		m = request.POST.get('model')
		self.id_seg = request.POST.get("id", ERROR)
		if self.id_seg == ERROR:
			self.id_seg = request.GET.get("id", ERROR)
		if self.id_seg == ERROR:
			redirect(VistaSegnalazioni)
		if m:
			mdl = getattr(gic.models, m)
			frm = type(form(mdl()))
			
		if self.action == ERROR:
			redirect(VistaSegnalazioni)
		elif self.action == SAVE:
			inst = mdl.objects.get(pk=request.POST.get('id'))
			f = frm(request.POST, instance = inst)
			if f.is_valid():
				f.save()
			self.action = START
		elif self.action == NEW:
				f = frm(request.POST)
#				frm.fields['stato'].required = False
				n_seg = f.save()
				self.action = START
				request.POST= {}
		return render(request, self.template_name, self.get_context_data(self, *args, **kwargs))

	def get_context_data(self, *args, **kwargs):
		
		segnalazione = Segnalazione.objects.get(id=self.id_seg)
		
		

		self.context['segnalazione'] = segnalazione
		self.context['action'] = self.action
		self.context['oggi'] = datetime.now()
		
		self.context["segnalazione_new"] = SegnalazioneForm
		self.context["intervento_new"] = InterventoForm
		self.context["team_new"] = TeamForm
		self.context['lavoro_new'] = LavoroForm
		self.context['gic_render'] = gic_render
		
		return self.context

"""

class VistaSingola_a(Vista_a):
	# template_name = "gic_intervento.html"
	action = ERROR
	id_s = ERROR
	redir = None
	
	def get(self, request, *args, **kwargs):
		self.id_s = request.GET.get("id", ERROR)
		if self.id_s == ERROR:
			redirect(self.redir)
		return render(request, self.template_name, self.get_context_data(self, *args, **kwargs))
	
	def post(self, request, *args, **kwargs):
		self.id_s = request.GET.get("id", ERROR)
		if self.id_s == ERROR:
			redirect(self.redir)
		v_tst = self.id_s
		self.action = request.POST.get('action', ERROR)
		m = request.POST.get('model')
		self.id_s = request.POST.get("id", ERROR)
		if self.id_s == ERROR:
			self.id_s = request.GET.get("id", ERROR)
		if self.id_s == ERROR:
			redirect(self.redir)
		if m:
			mdl = getattr(gic.models, m)
			frm = type(form(mdl()))
			
		if self.action == ERROR:
			redirect(self.redir)
		
		elif self.action == SAVE:
			inst = mdl.objects.get(pk=request.POST.get('id'))
			f = frm(request.POST, instance = inst)
			if f.is_valid():
				f.save()
			self.action = START
		
		elif self.action == NEW:
			f = frm(request.POST)
			n_seg = f.save()
			self.action = START
			request.POST= {}
		
		elif self.action == ALLEGATO:
			sg = Segnalazione.objects.get(id=request.POST["id_segnalazione"])
			alg = Allegato(
				descrizione = request.POST['descrizione'],
				segnalazione = sg,
				file = request.FILES["file"],
				)
			alg.save()
			request.POST={}

		elif self.action == VERIFICATO:
			inst = mdl.objects.get(pk=request.POST.get('id'))
			inst.stato = Tipologia.tipologia("TO", "VER")
			inst.save()
			self.action = START
			request.POST={}

		kwargs['id'] = v_tst 
		return render(request, self.template_name, self.get_context_data(self, *args, **kwargs))

		class Meta:
			abstract = True

class VistaIntervento(VistaSingola_a):
	template_name = "gic_intervento.html"
	redir = VistaInterventi
	
	def get_context_data(self, *args, **kwargs):
		
		id_r = self.id_s
		if "id" in kwargs:
			id_r = kwargs['id']
		intervento = Intervento.objects.get(id=id_r)
		
		

		self.context['intervento'] = intervento
		self.context['action'] = self.action
		self.context['oggi'] = timezone.now()
		
		self.context["intervento_new"] = InterventoForm
		self.context["team_new"] = TeamForm
		self.context['lavoro_new'] = LavoroForm
		self.context['gic_render'] = gic_render
		
		return self.context

class VistaSegnalazione(VistaSingola_a):
	template_name = "gic_segnalazione.html"
	redir = VistaSegnalazioni
	
	def get_context_data(self, *args, **kwargs):
		
		id_r = self.id_s
		if "id" in kwargs:
			id_r = kwargs['id']
		segnalazione = Segnalazione.objects.get(id=id_r)
		
		

		self.context['segnalazione'] = segnalazione
		self.context['action'] = self.action
		self.context['oggi'] = timezone.now()
		
		self.context["segnalazione_new"] = SegnalazioneForm
		self.context["intervento_new"] = InterventoForm
		self.context["team_new"] = TeamForm
		self.context['lavoro_new'] = LavoroForm
		self.context['gic_render'] = gic_render
		
		return self.context





class VistaOperaiLavoro(Vista_a):
	template_name="gic_operai_lavoro.html"
	action = START	
	debug = ""
	id_s = ERROR

	def setup(self, request, *args, **kwargs):
		super().setup(request, *args, **kwargs)
		#self.context['gic_render'][LAVORI_NEW] = False
	
	def post(self, request, *args, **kwargs):
		self.action = request.POST.get("action", START)
		self.id_s = request.POST.get("id_lavoro", self.id_s)
		#self.debug += self.action + " pre-if - "
		if  self.action in (TERMINA, PAUSA, AVVIA):
			#self.debug += self.action + " post-if - "
			tlv_attuale = None
			lv = Lavoro.objects.get(id=request.POST.get("id_lavoro"))
			for tlv in lv.tempilavoro_set.filter(fine__isnull=True).order_by("inizio"):
				tlv.fine = timezone.now()
				tlv.save()
				tlv_attuale = tlv
			if self.action == AVVIA:
				tl = TempiLavoro(lavoro=lv, note=request.POST.get("note"), inizio=timezone.now())
				tl.save()
				#self.debug += " in_avvio - "
			elif self.action in (TERMINA, PAUSA):
				tlv_attuale.note = request.POST.get("note", "-")
				tlv_attuale.save()
				if self.action == TERMINA:
					lv.stato = Tipologia.tipologia("TO", "CHI")
					lv.save()
					
		elif self.action == FOTO:
			#form = FotoForm(request.POST or None, request.FILES or None)
			
			lavoro = Lavoro.objects.get(id=request.POST.get('id_lavoro'))
			tipologia = Tipologia.objects.get(id=request.POST.get('tipo'))
			posizione = request.POST.get('posizione') 
			collaboratore= self.dipendente.collaboratore 
			intervento = lavoro.team.intervento
			note = request.POST.get('note')
			for img in request.FILES.getlist('foto'):
				foto = Foto(
					foto = img, 
					posizione = posizione, 
					tipologia = tipologia, 
					collaboratore = collaboratore, 
					intervento = intervento,
					note = note,
					)
				foto.save()
				#self.debug += " in_termine  - "
		elif self.action == ACCESSORIO:
			
			ass = Tipologia.objects.get(id=request.POST.get('stato'))
			col = Collaboratore.objects.get(id=request.POST.get('collaboratore'))
			tm = Team.objects.get(id=request.POST.get('team'))
			lavoro = Lavoro(
				oggetto= request.POST.get('oggetto'),
				descrizione = request.POST.get('descrizione'),
				durata_prevista = request.POST.get('durata_prevista'),
				stato = ass,
				collaboratore = col,
				team = tm,
				mod_priorita = request.POST.get('mod_priorita'),
				accessorio = True,
				)
			lavoro.save()
		elif self.action == URGENTE:
			coll = Collaboratore.objects.get(id=request.POST.get('collaboratore')),
			ass = Tipologia.tipologia("TO", "ASS")
			ogg = request.POST.get('oggetto')
			descrizione = request.POST.get('descrizione')
			durata_prevista = request.POST.get('durata_prevista')

			int = Intervento(
				oggetto = "INTERVENTO URGENTE: {o}".format(o = ogg),
				descrizione = "INTERVENTO URGENTE: {d}".format(d=descrizione),
				provvisorio = True,
				preposto = coll[0],
				note = "Intervento creato il {d} da {c}.".format(d=timezone.now(), c=coll[0]),
				priorita = Priorita.urgente()
	
			)
			int.save()

			tm = Team(
				attivita = Attivita.urgente(),
				intervento = int,
			)
			tm.save()
			
			lav = Lavoro(
				oggetto = ogg,
				descrizione = descrizione,
				durata_prevista = durata_prevista,
				stato = ass,
				collaboratore = coll[0],
				team = tm,
				mod_priorita = 1,
				accessorio = True,
			)
			lav.save()

		#self.debug += self.action + " fine post."
		self.action = START

		#request.POST= {}
		return render(request, self.template_name, self.get_context_data(self, *args, **kwargs))
	
	def get(self, request, *args, **kwargs):
		self.id_s = request.GET.get("id", ERROR)
		if self.id_s == ERROR:
			redirect(self.redir)
		return render(request, self.template_name, self.get_context_data(self, *args, **kwargs))
	
	def get_context_data(self, *args, **kwargs):
		
		id_r = self.id_s
		prova = self.id_s
		if "id" in kwargs:
			id_r = kwargs['id']
		if id_r == ERROR:
			# redirect(self.redir)
			pass
		else:
			lav = Lavoro.objects.get(id=id_r)
		
		self.context['lavoro'] = lav
		self.context['assegnato'] = Tipologia.t_stato("ASS")
		self.context['foto_form'] = FotoForm
		self.context['debug'] = self.debug
		self.context['gic_render'] = coll_render
		
		if self.dipendente.collaboratore.lavoro_attivo():
			tl = self.dipendente.collaboratore.lavoro_attivo().tempilavoro_set.filter(fine__isnull=True).order_by("-inizio")[0]
			delta = timezone.now() - tl.inizio
			self.context["delta"] = delta.seconds
		
		return self.context
	

class VistaOperai(VistaOperaiLavoro):
	template_name = "gic_operai.html"
	action = START
	debug = ""
	
	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data(self, *args, **kwargs))
	
	def get_context_data(self, *args, **kwargs):
		
		assegnati = Lavoro.lavori_da_svolgere(collaboratore=self.dipendente.collaboratore, pianificati=False)
		pianificati = Lavoro.lavori_da_svolgere(collaboratore=self.dipendente.collaboratore, pianificati=True)
		
		
		self.context['assegnato'] = Tipologia.t_stato("ASS")
		self.context['lavori'] = assegnati
		self.context['lavori_pianificati'] = pianificati
		self.context['foto_form'] = FotoForm
		self.context['debug'] = self.debug
		
		if self.dipendente.collaboratore.lavoro_attivo():
			tl = self.dipendente.collaboratore.lavoro_attivo().tempilavoro_set.filter(fine__isnull=True).order_by("-inizio")[0]
			delta = timezone.now() - tl.inizio
			self.context["delta"] = delta.seconds
		
		return self.context

class VistaReport(Vista_a):

	template_name = "gic_report.html"
	data_da = datetime.date(timezone.now().year, timezone.now().month, 1)
	data_a = last_day_of_month(data_da)

	def post(self, request, *args, **kwargs):
		oggi = datetime.date(timezone.now().year, timezone.now().month, 1)
		dt_da = request.POST.get('data_da', "{dt}".format(dt = oggi ))
		dt_a = request.POST.get('data_a', "{dt}".format(dt=last_day_of_month(oggi)))
		
		self.data_da=datetime.date(int(dt_da[0:4]), int(dt_da[5:7]), int(dt_da[8:10]))
		self.data_a=datetime.date(int(dt_a[0:4]), int(dt_a[5:7]), int(dt_a[8:10]))
		
		return render(request, self.template_name, self.get_context_data(self, *args, **kwargs))


	def get_context_data(self, *args, **kwargs):
		
		self.context['lavori'] = (Lavoro.lavori_data().exclude(data_fine__lt=self.data_da).exclude(data_inizio__gt=self.data_a).order_by('data_inizio') | Lavoro.lavori_data().filter(data_inizio__isnull=True)).distinct()
		self.context['data_da'] = "{dt}".format(dt=self.data_da)
		self.context['data_a'] = "{dt}".format(dt=self.data_a)
		
		return self.context
	
	
	
# class VistaReportCSV(VistaReport):
#     template_name = "gic_report.csv"
	
# def ReportCSVStream(request): #not working

# 	oggi = datetime.date(timezone.now().year, timezone.now().month, 1)
# 	dt_da = request.POST.get('data_da', "{dt}".format(dt = oggi ))
# 	dt_a = request.POST.get('data_a', "{dt}".format(dt=last_day_of_month(oggi)))
	
# 	data_da=datetime.date(int(dt_da[0:4]), int(dt_da[5:7]), int(dt_da[8:10]))
# 	data_a=datetime.date(int(dt_a[0:4]), int(dt_a[5:7]), int(dt_a[8:10]))
	
# 	lavs = Lavoro.lavori_data().exclude(data_fine__lt=data_da).exclude(data_inizio__gt=data_a).order_by('data_inizio')
# 	pseudo_buffer = Echo()
# 	writer = csv.writer(pseudo_buffer)
	
# 	return StreamingHttpResponse(
# 		(writer.writerow(lv.csv_row) for lv in lavs),
# 		content_type="text/csv",
# 		headers={"Content-Disposition": 'attachment; filename="report-{dt1}-{dt2}.csv"'.format(dt1=data_da, dt2=data_a)},
#     )


def ReportCSV(request):
	oggi = datetime.date(timezone.now().year, timezone.now().month, 1)
	dt_da = request.POST.get('data_da', "{dt}".format(dt = oggi ))
	dt_a = request.POST.get('data_a', "{dt}".format(dt=last_day_of_month(oggi)))
	return ReportCSVDt(request, dt_da, dt_a)

def ReportCSVDt(request, dt_da, dt_a):

	humanize.i18n.activate("it_IT")

	data_da=datetime.date(int(dt_da[0:4]), int(dt_da[5:7]), int(dt_da[8:10]))
	data_a=datetime.date(int(dt_a[0:4]), int(dt_a[5:7]), int(dt_a[8:10]))
	
	lavs = (Lavoro.lavori_data().exclude(data_fine__lt=data_da).exclude(data_inizio__gt=data_a).order_by('data_inizio') | Lavoro.lavori_data().filter(data_inizio__isnull=True)).distinct()
	response = HttpResponse(
		content_type="text/csv",
		headers={"Content-Disposition": 'attachment; filename="report-{dt1}-{dt2}.csv"'.format(dt1=data_da, dt2=data_a)},
	)
	writer = csv.writer(response, dialect="excel")
	#writer.writerow(["dt_da",dt_da, "dt_a", last_day_of_month(dt_a), "data_da", "{d}".format(d= data_da), "data_a", "{d}".format(d= data_a),])
	writer.writerow([
		"Oggetto", 
		"Descrizione", 
		"incaricato", 
		"Prima attività", 
		"Ultima attività", 
		"Stato del Lavoro", 
		"Minuti totali",
		"Tempo totale", 
		"Allegati", 
		"Foto", 
		"Attivo", 
		"ID Intervento", 
		"Oggetto Intervento", 
		"Team di Intervento",
		"data Segnalazione",
		"Struttura", 
		"Segnalatore",
		"CdC",
		"ID Segnalazione",
		"Oggetto Segnalazione",
		"Tipo Segnalazione",
		"Tags",
	])
	for lav in lavs:
		tags = ""
		allegato_count = 0
		seg_data= ""
		seg_struttura = ""
		seg_segnalatore = ""
		seg_cdc = ""
		seg_id = ""
		seg_oggetto = ""
		seg_tipo = ""
		if lav.team.intervento.segnalazione:
			for tg in lav.team.intervento.segnalazione.tags.all():
				tags += tg.nome_breve + "|"
			allegato_count = lav.team.intervento.segnalazione.allegato_set.count()
			seg_data = "{d}".format(d=lav.team.intervento.segnalazione.data_creazione)
			seg_struttura = lav.team.intervento.segnalazione.struttura .__str__()
			seg_segnalatore = lav.team.intervento.segnalazione.segnalatore.__str__()
			seg_cdc = lav.team.intervento.segnalazione.struttura.cdc.__str__()
			seg_id = lav.team.intervento.segnalazione.id
			seg_oggetto = lav.team.intervento.segnalazione.oggetto
			seg_tipo = lav.team.intervento.segnalazione.tipo.__str__()
	
		writer.writerow([
				lav.oggetto, 
				lav.descrizione,
				lav.collaboratore,
				lav.data_inizio,
				lav.data_fine,
				lav.stato,
				lav.minuti_totali,
				lav.tempo_totale_h,
				allegato_count,
				lav.team.intervento.foto_set.count(),
				lav.attivo,
				lav.team.intervento.id,
				lav.team.intervento.oggetto,
				lav.team.attivita,
				seg_data,
				seg_struttura,
				seg_segnalatore,
				seg_cdc,
				seg_id,
				seg_oggetto,
				seg_tipo,
				tags,
			])
	return response


class VistaStrutture(Vista_a):
	template_name = "gic_strutture.html"
	action = START	
	debug = ""
	id_s = ERROR
	
	def post(self, request, *args, **kwargs):
		self.action = request.POST.get("action", START)
		self.id_s = request.POST.get("id_lavoro", self.id_s)
  
		if self.action == NEW:
			segn = Segnalazione(
				tipo = Tipologia.tipologia(request.POST.get("tipo")[0:2], request.POST.get("tipo")[3:6]),
				stato = Tipologia.tipologia(request.POST.get("stato")[0:2], request.POST.get("stato")[3:6]),
				origine = Tipologia.tipologia(request.POST.get("origine")[0:2], request.POST.get("origine")[3:6]),
				segnalatore = request.POST.get("segnalatore"),
				email = request.POST.get("email"),
				telefono = request.POST.get("telefono"),
				oggetto = request.POST.get("oggetto"),
				descrizione = request.POST.get("descrizione"),
				struttura = Struttura.objects.get(id = request.POST.get("struttura")),
				data_pianificazione = timezone.now(),
    
			)
			segn.save()

			for img in request.FILES.getlist('foto'):
				allg = Allegato(
					file = img, 
					segnalazione = segn,
					)
				allg.save()


		

		#self.debug += self.action + " fine post."
		self.action = START

		#request.POST= {}
		return render(request, self.template_name, self.get_context_data(self, *args, **kwargs))


	def get_context_data(self, *args, **kwargs):
		
		strutts = self.context["dipendente"].servizio_al().strutture.all()
		self.context["strutture"] = strutts
		self.context["segnalazioni"] = Segnalazione.objects.filter(struttura__in = strutts).exclude(stato__in = (Tipologia.t_stato("CHI"), Tipologia.t_stato("VER")))
		self.context["segnalazione_new"] = SegnalazioneStrutturaForm
		self.context['gic_render'] = str_render




class TemaViewSet(viewsets.ModelViewSet):
	queryset = Tema.objects.all()
	serializer_class = TemaSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['modello', 'tema']

class VistaViewSet(viewsets.ModelViewSet):
	queryset = Vista.objects.all()
	serializer_class = VistaSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['nome', 'nome_modello', ]


class MansioneViewSet(viewsets.ModelViewSet):
	queryset = Mansione.objects.all()
	serializer_class = MansioneSerializer
	authentication_classes = (TokenAuthentication,)
	# filter_backends = [DjangoFilterBackend]
	# filterset_fields = ['nome', 'descrizione', 'tema']

class MansioneTranslationViewSet(viewsets.ModelViewSet):
	queryset = MansioneTranslation.objects.all()
	serializer_class = MansioneTranslationSerializer
	authentication_classes = (TokenAuthentication,)
	# filter_backends = [DjangoFilterBackend]
	# filterset_fields = ['nome', 'descrizione', 'tema']

class AttivitaViewSet(viewsets.ModelViewSet):
	queryset = Attivita.objects.all()
	serializer_class = AttivitaSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['obbligo_foto', 'chiusura_auto_lavoro', 'mansioni']

class AttivitaTranslationViewSet(viewsets.ModelViewSet):
	queryset = AttivitaTranslation.objects.all()
	serializer_class = AttivitaTranslationSerializer
	authentication_classes = (TokenAuthentication,)
	# filter_backends = [DjangoFilterBackend]
	# filterset_fields = ['nome', 'descrizione', 'tema']

class PrioritaViewSet(viewsets.ModelViewSet):
	queryset = Priorita.objects.all()
	serializer_class = PrioritaSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['valore', ]

class PrioritaTranslationViewSet(viewsets.ModelViewSet):
	queryset = PrioritaTranslation.objects.all()
	serializer_class = PrioritaTranslationSerializer
	authentication_classes = (TokenAuthentication,)
	# filter_backends = [DjangoFilterBackend]
	# filterset_fields = ['nome', 'descrizione', 'valore']

class AnnoViewSet(viewsets.ModelViewSet):
	queryset = Anno.objects.all()
	serializer_class = AnnoSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['anno', ]

class SquadraViewSet(viewsets.ModelViewSet):
	queryset = Squadra.objects.all()
	serializer_class = SquadraSerializer
	authentication_classes = (TokenAuthentication,)
	# filter_backends = [DjangoFilterBackend]
	# filterset_fields = ['nome', 'descrizione', 'tema']

class SquadraTranslationViewSet(viewsets.ModelViewSet):
	queryset = SquadraTranslation.objects.all()
	serializer_class = SquadraTranslationSerializer
	authentication_classes = (TokenAuthentication,)
	# filter_backends = [DjangoFilterBackend]
	# filterset_fields = ['nome', 'descrizione', 'tema']

class TipologiaViewSet(viewsets.ModelViewSet):
	queryset = Tipologia.objects.all()
	serializer_class = TipologiaSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['tipo', 'abbreviazione', 'ordine',]

class TipologiaTranslationViewSet(viewsets.ModelViewSet):
	queryset = TipologiaTranslation.objects.all()
	serializer_class = TipologiaTranslationSerializer
	authentication_classes = (TokenAuthentication,)
	# filter_backends = [DjangoFilterBackend]
	# filterset_fields = ['nome', 'descrizione', 'abbreviazione', 'tema']

class CollaboratoreViewSet(viewsets.ModelViewSet):
	queryset = Collaboratore.objects.all()
	serializer_class = CollaboratoreSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['dipendente', 'squadra', 'responsabile', 'mansioni', 'assenze', 'reperibilita']

class CdCViewSet(viewsets.ModelViewSet):
	queryset = CdC.objects.all()
	serializer_class = CdCSerializer
	authentication_classes = (TokenAuthentication,)
	# filter_backends = [DjangoFilterBackend]
	# filterset_fields = ['nome', 'descrizione', 'tema']

class CdCTranslationViewSet(viewsets.ModelViewSet):
	queryset = CdCTranslation.objects.all()
	serializer_class = CdCTranslationSerializer
	authentication_classes = (TokenAuthentication,)
	# filter_backends = [DjangoFilterBackend]
	# filterset_fields =	 ['nome', 'descrizione', 'tema']
 

class StrutturaViewSet(viewsets.ModelViewSet):
	queryset = Struttura.objects.all()
	serializer_class = StrutturaSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['responsabile', 'cdc', 'autorizzati', ]

class StrutturaTranslationViewSet(viewsets.ModelViewSet):
	queryset = StrutturaTranslation.objects.all()
	serializer_class = StrutturaTranslationSerializer
	authentication_classes = (TokenAuthentication,)
	# filter_backends = [DjangoFilterBackend]
	# filterset_fields = ['nome', 'descrizione', 'tema', 'cdc']

class DirittoViewSet(viewsets.ModelViewSet):
	queryset = Diritto.objects.all()
	serializer_class = DirittoSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['nome', 'capocantiere', 'caposquadra', 'coordinatore', 'operaio', 'struttura', 'ufficio',]

class EventoViewSet(viewsets.ModelViewSet):
	queryset = Evento.objects.all()
	serializer_class = EventoSerializer
	authentication_classes = (TokenAuthentication,)
	# filter_backends = [DjangoFilterBackend]
	# filterset_fields = ['nome', 'descrizione', 'tema', 'priorita', 'stato']

class TagViewSet(viewsets.ModelViewSet):
	queryset = Tag.objects.all()
	serializer_class = TagSerializer
	authentication_classes = (TokenAuthentication,)
	# filter_backends = [DjangoFilterBackend]
	# filterset_fields = ['nome', 'descrizione', 'tema']

class EventoTranslationViewSet(viewsets.ModelViewSet):
	queryset = EventoTranslation.objects.all()
	serializer_class = EventoTranslationSerializer
	authentication_classes = (TokenAuthentication,)
	# filter_backends = [DjangoFilterBackend]
	# filterset_fields = ['nome', 'descrizione', 'tema', 'priorita', 'stato']

#----- Segnalazioni -----

class SegnalazioneViewSet(viewsets.ModelViewSet):
	queryset = Segnalazione.objects.exclude(stato__abbreviazione="VER").distinct()
	serializer_class = SegnalazioneSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['stato', 'origine', 'segnalatore', 'struttura', 'data_creazione', 'data_pianificazione', 'eventi', 'tags', 'tipo',  ]


class SegnalazioneCompletaViewSet(viewsets.ModelViewSet):
	queryset = Segnalazione.objects.exclude(stato__abbreviazione="VER").distinct()
	serializer_class = SegnalazioneCompletaSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['stato', 'origine', 'segnalatore', 'struttura', 'data_creazione', 'data_pianificazione', 'eventi', 'tags', 'tipo', ]
 

 
class SegnalazioneStoricaViewSet(viewsets.ModelViewSet):
	queryset = Segnalazione.objects.filter(stato__abbreviazione="VER").distinct()
	serializer_class = SegnalazioneSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['stato', 'origine', 'segnalatore', 'struttura', 'data_creazione', 'data_pianificazione', 'eventi', 'tags', 'tipo', ]

class SegnalazioneStoricaCompletaViewSet(viewsets.ModelViewSet):
	queryset = Segnalazione.objects.filter(stato__abbreviazione="VER")
	serializer_class = SegnalazioneCompletaSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['stato', 'origine', 'segnalatore', 'struttura', 'data_creazione', 'data_pianificazione', 'eventi', 'tags', 'tipo', ]

#----- Interventi -----
class InterventoViewSet(viewsets.ModelViewSet):
	queryset = Intervento.objects.all()
	serializer_class = InterventoSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['segnalazione', 'stato', 'priorita', 'preposto', 'provvisorio', 'struttura', ]

class TeamViewSet(viewsets.ModelViewSet):
	queryset = Team.objects.all()
	serializer_class = TeamSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['attivita', 'intervento', ]

class FotoViewSet(viewsets.ModelViewSet):
	queryset = Foto.objects.all()
	serializer_class = FotoSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['tipologia', 'collaboratore', 'intervento', 'posizione', ]

class LavoroViewSet(viewsets.ModelViewSet):
	queryset = Lavoro.objects.all()
	serializer_class = LavoroSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['collaboratore', 'team', 'caposquadra', 'stato', 'accessorio', 'urgenza', ]

class TempiLavoroViewSet(viewsets.ModelViewSet):
	queryset = TempiLavoro.objects.all()
	serializer_class = TempiLavoroSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['lavoro', 'inizio', 'fine', ]

class AllegatoViewSet(viewsets.ModelViewSet):
	queryset = Allegato.objects.all()
	serializer_class = AllegatoSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['segnalazione', 'descrizione', 'data_creazione']
class AnnotazioneViewSet(viewsets.ModelViewSet):
	queryset = Annotazione.objects.all()
	serializer_class = AnnotazioneSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['lavoro',  'data_creazione']

class EventoSegnalazioneViewSet(viewsets.ModelViewSet):
	queryset = EventoSegnalazione.objects.all()
	serializer_class = EventoSegnalazioneSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['segnalazione', 'evento', 'data_creazione', ]

class CollaboratoreMansioneViewSet(viewsets.ModelViewSet):
	queryset = CollaboratoreMansione.objects.all()
	serializer_class = CollaboratoreMansioneSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['collaboratore', 'mansione', 'data_da', 'data_a', ]

class CollaboratoreAssenzaViewSet(viewsets.ModelViewSet):
	queryset = CollaboratoreAssenza.objects.all()
	serializer_class = CollaboratoreAssenzaSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['collaboratore', 'data_da', 'data_a', 'assenza', ]

class CollaboratoreReperibilitaViewSet(viewsets.ModelViewSet):
	queryset = CollaboratoreReperibilita.objects.all()
	serializer_class = CollaboratoreReperibilitaSerializer
	authentication_classes = (TokenAuthentication,)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['collaboratore', 'data_da', 'data_a', 'reperibilita', ]

class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	authentication_classes = (TokenAuthentication,)
	permission_classes = (permissions.IsAuthenticated, )
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['username', 'email', 'first_name', 'last_name']
    

class AuthTokenViewSet(viewsets.ViewSet):
	serializer_class = AuthTokenSerializer
	permission_classes = (permissions.AllowAny,)

	def create(self, request):
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)

		user = authenticate(
			request=request,
			username=serializer.validated_data['username'],
			password=serializer.validated_data['password']
		)

		if not user:
			return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

		token, created = Token.objects.get_or_create(user=user)
		return Response({'token': token.key})
