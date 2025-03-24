from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime

from .models import Delega, GruppoPratica, Dipendente_GruppoPratica, TipoPratica
from dipendenti.models import Dipendente, Logo


# Create your views here.

def InserisciFerie(request):
	sett = int(request.POST['setferie'])
	user = request.user
	logdip = Dipendente.objects.get(userid=user.username)
	
	dip_grp = Dipendente_GruppoPratica.objects.filter(dipendente=logdip)
	txt = "Ferie - inserite da {cognome} {nome}"
	
	deleg = Delega(documento="-", 
				tipo_pratica=TipoPratica.objects.get(id=5), # 5 è la tipologia di documenti di tipo "ferie"
				peso= 5 * sett, 
				gruppo=dip_grp[0].gruppopratica, 
				assegnatario = logdip,
				note="Inserimento Ferie",
				origine=txt.format(cognome=logdip.cognome.upper(), nome=logdip.nome),
	)
	deleg.save()
	
	return redirect('http://leifersdjango.leifers.gvcc.net/pratiche/lista/')	

def PraticaUfficio(request):
	dip = Dipendente.objects.get(id=request.POST['dipendente'])
	ID_documento = request.POST['ID_documento']
	val_peso = request.POST['peso']
	note_p = request.POST['note']
	user = request.user
	logdip = Dipendente.objects.get(userid=user.username)
	grps = GruppoPratica.objects.filter(responsabile__id=logdip.id)
	gruppi = GruppoPratica.objects.filter(delegato=dip)
	txt = "assegnazione d'ufficio - {cognome} {nome}"
	note_tot = "Assegnazione d'ufficio"
	if note_p:
		note_tot = note_tot + "\n" + note_p

	deleg = Delega(documento=ID_documento, 
				tipo_pratica=TipoPratica.objects.get(id=1), # 1 è la tipologia di documenti di tipo "documento generico"
				peso=val_peso, 
				gruppo=gruppi[0], 
				assegnatario = dip,
				note=note_tot,
				origine=txt.format(cognome=logdip.cognome.upper(), nome=logdip.nome),
	)
	deleg.save()
	return redirect('http://leifersdjango.leifers.gvcc.net/pratiche/lista/')
	

def CompletaPratica(request, id_delega):
	deleg = Delega.objects.filter(id=id_delega)
	deleg.update(completato=True, data_completamento = datetime.datetime.now())
	return redirect('http://leifersdjango.leifers.gvcc.net/pratiche/lista/')

class VistaTecnici(LoginRequiredMixin, TemplateView):
	template_name = "lista.html"
	
	loggeduser = None
	dipendente = None
	respgruppo = False
	gestgruppo = False 
	
	def get(self, request, *args, **kwargs):
		self.loggeduser = request.user
		if "_leifers" in self.loggeduser.username:
			self.dipendente = Dipendente.objects.get(userid=self.loggeduser.username)
		return super().get(request, *args, **kwargs)
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['user'] = self.loggeduser
		context['dipendente'] = self.dipendente
		context['logo'] = Logo.objects.get(id=1)
		deleghe = None
		if self.dipendente is None:
			pass
		else:
			deleghe = Delega.objects.filter(assegnatario__exact=self.dipendente.id).exclude(system=True).exclude(completato=True).order_by('data_assegnazione')
	
		context['deleghe'] = deleghe 
		
		grps = GruppoPratica.objects.filter(responsabile__id=self.dipendente.id)
		if len(grps)==1:
			self.respgruppo=True
		#gruppi = GruppoPratica.objects.filter(delegato=self.dipendente)
		gruppi_gestiti = []
		for g in GruppoPratica.objects.all():
			if self.dipendente in g.gestori.all():
				self.gestgruppo=True
				gruppi_gestiti.append(g)
		
		
		context['respgruppo'] = self.respgruppo
		context['dip_gp'] = Dipendente_GruppoPratica.objects.filter(gruppopratica__in=grps)
		context['gruppi_gestiti'] = gruppi_gestiti
		context['gestgruppo'] = self.gestgruppo
		
		return context