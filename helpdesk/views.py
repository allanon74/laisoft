from django.shortcuts import render
from django.shortcuts import redirect
from django.template.loader import get_template
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
import datetime
import requests
from django.urls import reverse_lazy
from django.utils import timezone

from .models import Ticket, Azione, Tipologia, Allegato
from dipendenti.models import Dipendente, Logo
from dipendenti.views import base_context
from .forms import FormAllegato
from webpush import send_user_notification

# Create your views here.

#

#def visualizza_ticket(request, id_ticket):

#	templ = 'dettaglio_ticket.html'
#	context = {'Author':'giorgio_leifers'}
#	context['id_ticket'] = id_ticket
#	return render(request, templ, context)

ADMIN_GROUP = "LS_helpdesk_admin"

#BASE_URL = settings.BASE_URL

def wiki(request):
	response = redirect('http://wikilaives/mediawiki/index.php/Pagina_principale')
	return response

def lista(request):

	response = redirect('/helpdesk/lista/')
	return response

def inserisci_ticket(request):
	loggeduser = request.user
	tipologia = request.POST['tipologia']
	persona = request.POST['persona']
	tst = request.POST['testo']
	
	tip = Tipologia.objects.get(id=tipologia)
	#ut = User.objects.get(username=persona)
	di = Dipendente.objects.get(userid=persona)

	
	tick = Ticket(tipologia=tip, persona=di, testo=tst, utente_apertura=loggeduser, utente_modifica=loggeduser)
	tick.save()
	
# 	msg = {'head': "Nuovo ticket", 'body': "è arrivato un nuovo ticket:{titolo}".format(titolo=tick.nome)}
# 	for dip in tick.tipologia.gruppo.membri.all():
# 		usr = User.objects.get(username=dip.userid)
# 		send_user_notification(usr, payload=msg, ttl=1000)


	return redirect('/helpdesk/lista/')
	
def form_inserisci_ticket(request):
	templ = 'inserisci_ticket.html'
	
	loggeduser = request.user
	dipendente = None
	admin = False
	
	if "_leifers" in loggeduser.username:
		dipendente = Dipendente.objects.get(userid=loggeduser.username)
	admin = loggeduser.groups.filter(name=ADMIN_GROUP).exists()
	
	username=loggeduser.username
	
	context = base_context(request)
	context['tipologie'] = Tipologia.objects.all().order_by('nome')
	context['admin'] = admin
	context['loggeduser'] = loggeduser
	
	context['loggeddipendente'] = dipendente
	context['username'] = loggeduser.username
	context['userid'] = dipendente.userid
	
	context['dipendenti'] = Dipendente.objects.filter(attivo=True).order_by('cognome', 'nome')
	
	return render(request, templ, context)

def risolvi_ticket(request):
	id_ticket = request.POST["id_ticket"]
	tick = Ticket.objects.get(id=id_ticket)
	tick.soluzione = request.POST['soluzione']
	tick.data_chiusura = datetime.datetime.now()
	tick.utente_chiusura = request.user
	tick.chiuso = True
	tick.save()
	request.path = "/helpdesk/lista/dettaglio/"
	return visualizza_ticket(request)

def aggiungi_azione(request):
	id_ticket = request.POST["id_ticket"]
	tick = Ticket.objects.get(id=id_ticket) 
	az = Azione(ticket=tick, data_azione= datetime.datetime.now(), utente= request.user, nota=request.POST["nota"])
	az.save()
	tick.utente_modifica = request.user
	tick.save()
	request.path = "/helpdesk/lista/dettaglio/"
#	return visualizza_ticket(request)
#	return redirect('visualizza_ticket', request)

	return requests.post('/helpdesk/lista/dettaglio/', data={'id_ticket':id_ticket})
	

def visualizza_ticket(request):

	templ = 'dettaglio_ticket.html'
	to_do = request.POST.get('to_do', "none")
	azione_interna = False
	
	form_allegato = FormAllegato(request.POST, request.FILES)
	
	id_ticket = request.POST["id_ticket"]
	loggeduser = request.user
	dipendente = None
	admin = False
	
	if "_leifers" in loggeduser.username:
		dipendente = Dipendente.objects.get(userid=loggeduser.username)
	admin = loggeduser.groups.filter(name=ADMIN_GROUP).exists()

	tick = Ticket.objects.get(id=id_ticket)
	
#	logo = Logo.objects.get(id=2)
	
	
	if to_do == 'azione' or to_do == 'incarico':
		int = request.POST.get("tipologia", "-")
		if int == "interna":
			azione_interna = True
		act = Azione(ticket=tick, data_azione= datetime.datetime.now(), utente= request.user, nota=request.POST["nota"], interna=azione_interna)
		act.save()
		if not azione_interna:
			if admin:
				act.mail_azione(edp=True)
			else:
				act.mail_azione(edp=False)
		tick.utente_modifica = request.user
		if to_do == 'incarico':
			tick.incaricato = dipendente
		tick.save()

	elif to_do == 'soluzione':
		tick.soluzione = request.POST['soluzione']
		tick.data_chiusura = datetime.datetime.now()
		tick.utente_chiusura = request.user
		tick.chiuso = True
		tick.save()

	elif to_do == 'allegato':
		if form_allegato.is_valid():
			allg = Allegato(ticket=tick, nome=request.POST['nome'], file = request.FILES['file'])
			allg.save()

	alleg = False
	allegati = tick.allegato_set.all()
	if allegati.count() >0:
		alleg = True
	
	az = False
	azioni = tick.azioni_rel.all().order_by('-data_azione')
	if not admin:
		azioni = azioni.filter(interna=False)
	if azioni.count() >0:
		az=True
	
	context = base_context(request)
#	context['logo'] = logo
	context['id_ticket'] = id_ticket
	context['user'] = loggeduser
	context['dipendente'] = dipendente
	context['admin'] = admin
	context['ticket'] = tick
	context['alleg'] = alleg
	context['allegati'] = allegati
	context['azioni'] = azioni
	context['az'] = az
	context['form_allegato'] = form_allegato
	return render(request, templ, context)

# classe astratta per le viste




class Vista_abstract(LoginRequiredMixin, TemplateView):
	loggeduser = None
	dipendente = None
	admin = False
	context = {}
	login_url = reverse_lazy('users:login')
	
	def setup(self, request, *args, **kwargs):
		super().setup(request, *args, **kwargs)
		self.context = base_context(request, super().get_context_data())
		self.loggeduser = self.context['loggeduser']
		self.dipendente = self.context['dipendente']
		self.admin = self.context['admin']


	
	class Meta:
		abstract = True

# Classi di vista 


class VistaTicket(Vista_abstract):
	template_name = "lista_ticket.html"
	chiusi = "no"
	context = {}
	#req = None
	
	def get(self, request, *args, **kwargs):
		self.loggeduser = request.user
		self.chiusi = request.GET.get("chiusi", "no")
		if "_leifers" in self.loggeduser.username:
			self.dipendente = Dipendente.objects.get(userid=self.loggeduser.username)
		self.admin = self.loggeduser.groups.filter(name=ADMIN_GROUP).exists()
		#req = request
		return super().get(request, *args, **kwargs)
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		context['user'] = self.loggeduser
		context['dipendente'] = self.dipendente
		context['admin'] = self.admin
		context['logo'] = Logo.objects.get(id=1)
		
		ticks = None
		if self.chiusi == "yes":
			ticks = Ticket.objects.filter(chiuso = True)
		else:
			ticks = Ticket.objects.filter(chiuso = False)
		
		personal = ticks.filter(persona=self.dipendente)
		if  self.admin:
			
			ticks = ticks.filter(tipologia__gruppo__in = self.dipendente.grupposupporto_set.all()).union(personal)
		else:
			ticks = personal
		
		context['tickets'] = ticks.order_by('chiuso','-data_apertura')
		
		
		return context
	
class VistaDettaglioTicket(Vista_abstract):
	template_name = "dettaglio_ticket.html"
	id_ticket = None
	form_allegato = FormAllegato()
	
	def post(self, request, *args, **kwargs):
		sec = ""
		if request.is_secure():
			sec = "s"
		self.context['base_url'] = 'http:{secure}//{base}/'.format(base=request.get_host(), secure=sec)
		self.context['action'] = request.POST.get('to_do', None)
		if self.id_ticket == None:
			self.id_ticket = request.POST.get("id_ticket", None)
		self.context['azione_interna'] = (request.POST.get('tipologia', '-') == "interna")
		if self.id_ticket:
			tick = Ticket.objects.get(id=self.id_ticket)
			self.context['ticket'] = tick
			self.form_allegato = FormAllegato(request.POST, request.FILES)
			# request['form_allegato'] = form_allegato
			if self.context['action'] == None:
				pass
			elif self.context['action'] == "azione" or self.context['action'] == "incarico":
				act = Azione(ticket=tick, data_azione= timezone.now(), utente= request.user, nota=request.POST["nota"], interna=self.context['azione_interna'])
				act.save()
				if not self.context['azione_interna']:
					act.mail_azione(edp = self.context['admin'])
				tick.utente_modifica = request.user
				if self.context['action'] == 'incarico':
					tick.incaricato = self.context['dipendente']
				tick.save()
			elif self.context['action'] == 'soluzione':
				tick.soluzione = request.POST['soluzione']
				tick.data_chiusura = timezone.now()
				tick.utente_chiusura = request.user
				tick.chiuso = True
				tick.save()
			elif self.context['action'] == 'allegato':
				if self.form_allegato.is_valid():
					allg = Allegato(ticket=tick, nome=request.POST['nome'], file = request.FILES['file'])
					allg.save()
			#redirect('{base}helpdesk/lista/dettaglio/?id_ticket={id_tick}'.format(base=BASE_URL, id_tick=self.id_ticket))
			
		return render(request, self.template_name, self.get_context_data())
	
	
	def get(self, request, *args, **kwargs):
		if self.id_ticket == None:
			self.id_ticket = request.GET.get("id_ticket", None)
		if self.id_ticket:
			tick = Ticket.objects.get(id=self.id_ticket)
			self.context['ticket'] = tick
		return render(request, self.template_name, self.get_context_data())
	
	
	def get_context_data(self, **kwargs):
		t = self.id_ticket
		tick = Ticket.objects.get(id=self.id_ticket)
		self.context['ticket'] = tick 
		alleg = False
		allegati = tick.allegato_set.all()
		if allegati.count() >0:
			alleg = True
		
		az = False
		azioni = tick.azioni_rel.all().order_by('-data_azione')
		if not self.admin:
			azioni = azioni.filter(interna=False)
		if azioni.count() >0:
			az=True
		
		self.context['id_ticket'] = self.id_ticket
		#self.context['base_url'] = BASE_URL
		self.context['id_ticket'] = self.id_ticket
		self.context['alleg'] = alleg
		self.context['allegati'] = allegati
		self.context['azioni'] = azioni
		self.context['az'] = az
		self.context['form_allegato'] = self.form_allegato
		
		return self.context