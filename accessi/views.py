from django.shortcuts import render
from django_renderpdf.views import PDFView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin

from dipendenti.models import Dipendente, Logo
from dipendenti.views import base_context

from .models import TipoGenerico, AmbitiPassword, TestoFisso, Share, Atto, Password, Designazione, Autorizzazione
from .models import GruppoSamba, SGVCanale, GOffice, D3Diritto, Generico, DirittoRete, O365Gruppo, NextCloud, Porta, WebApp, GebevDiritto, GebevRipartizione, D3Gruppo, Web
from .models import Atto_GruppoSamba, Atto_SGVCanale, Atto_GOffice, Atto_D3Diritto, Atto_Generico, Atto_DirittoRete, Atto_D3Gruppo
from .models import Atto_O365Gruppo, Atto_NextCloud, Atto_Porta, Atto_WebApp, Atto_GebevDiritto, Atto_GebevRipartizione, Atto_Web

from .models import Autorizzazione_GruppoSamba, Autorizzazione_SGVCanale, Autorizzazione_GOffice, Autorizzazione_D3Diritto, Autorizzazione_Generico, Autorizzazione_DirittoRete, Autorizzazione_D3Gruppo
from .models import Autorizzazione_O365Gruppo, Autorizzazione_NextCloud, Autorizzazione_Porta, Autorizzazione_WebApp, Autorizzazione_GebevDiritto, Autorizzazione_GebevRipartizione, Autorizzazione_Web, Autorizzazione_GOffice2

# Create your views here.

class StampaDesignazione(LoginRequiredMixin, PDFView):
	template_name = 'designazione_pr.html'
	prompt_download = True
	base_name = "Designazione autorizzati - {cognome} {nome} ({matricola}) - {data:%d/%m/%Y}.pdf"
	download_name = "Designazione.pdf"
	
	def get_context_data(self, *args, **kwargs):
		atto = Atto.objects.get(id=kwargs['id'], )
		context = super().get_context_data(*args, **kwargs)
		context['atto'] = atto
		context['ufficio'] = atto.dipendente.ufficio_al(atto.data)
		context['capoversi'] = atto.designazione.testo.capoverso_set.all().order_by('ordine')
		
		self.download_name = self.base_name.format(
			cognome=atto.dipendente.cognome,
			nome=atto.dipendente.nome,
			matricola=atto.dipendente.matricola,
			data=atto.data
			)
		return context
	
class StampaPassword(LoginRequiredMixin, PDFView):
	template_name = 'password_pr.html'
	prompt_download = True
	base_name = "Attribuzione password - {cognome} {nome} ({matricola}) - {data:%d/%m/%Y}.pdf"
	download_name = "Password.pdf"
	
	def get_context_data(self, *args, **kwargs):
		atto = Atto.objects.get(id=kwargs['id'], )
		context = super().get_context_data(*args, **kwargs)
		context['atto'] = atto
		context['ufficio'] = atto.dipendente.ufficio_al(atto.data)
		context['capoversi'] = atto.password.testo.capoverso_set.all().order_by('ordine')
		
		self.download_name = self.base_name.format(
			cognome=atto.dipendente.cognome,
			nome=atto.dipendente.nome,
			matricola=atto.dipendente.matricola,
			data=atto.data
			)
		return context
	
class StampaAmbito(LoginRequiredMixin, PDFView):
	template_name = 'ambito_pr.html'
	prompt_download = True
	base_name = "Ambito del trattamento - {cognome} {nome} ({matricola}) - {data:%d/%m/%Y}.pdf"
	download_name = "Ambito.pdf"
	
	def get_context_data(self, *args, **kwargs):
		atto = Atto.objects.get(id=kwargs['id'], )
		
		if atto.dirigente_alt == None:
			dirigente = atto.dipendente.dirigente_al(atto.data)
			if dirigente == atto.dipendente:
				if atto.dipendente == Dipendente.segretario_al(atto.data):
					dirigente = Dipendente.sindaco_al(atto.data)
				else:
					dirigente = Dipendente.segretario_al(atto.data)
		else:
			dirigente = atto.dirigente_alt
		context = super().get_context_data(*args, **kwargs)
		context['atto'] = atto
		context['ufficio'] = atto.dipendente.ufficio_al(atto.data)
		context['capoversi'] = atto.password.testo.capoverso_set.all().order_by('ordine')
		context['dirigente'] = dirigente
		
		self.download_name = self.base_name.format(
			cognome=atto.dipendente.cognome,
			nome=atto.dipendente.nome,
			matricola=atto.dipendente.matricola,
			data=atto.data
			)
		return context

class StampaAutorizzazione(LoginRequiredMixin, PDFView):
	template_name = 'autorizzazione_pr.html'
	prompt_download = True
	base_name = 'Autorizzazione generale - {uff} - {data:%d/%m/%Y}.pdf'
	download_name = 'autorizzazione.pdf'
	
	def get_context_data(self, *args, **kwargs):
		autz = Autorizzazione.objects.get(id=kwargs['id'], )
		if autz.dirigente_alt == None:
			dirigente = autz.ufficio.dirigente_al(autz.data)

		else:
			dirigente = autz.dirigente_alt

		context = super().get_context_data(*args, **kwargs)
		context['autorizzazione'] = autz
		context['ufficio'] = autz.ufficio
		context['capoversi'] = autz.testo.capoverso_set.all().order_by('ordine')
		context['dirigente'] = dirigente
		
		context['gruppisamba'] = Autorizzazione_GruppoSamba.objects.filter(autorizzazione=autz).order_by('diritto__tipologia')
		context['sgvcanali'] = Autorizzazione_SGVCanale.objects.filter(autorizzazione=autz)
		context['goffice'] = Autorizzazione_GOffice.objects.filter(autorizzazione=autz)
		context['d3gruppi'] = Autorizzazione_D3Gruppo.objects.filter(autorizzazione=autz)
		context['d3diritti'] = Autorizzazione_D3Diritto.objects.filter(autorizzazione=autz)
		context['generici'] = Autorizzazione_Generico.objects.filter(autorizzazione=autz)
		context['dirittirete'] = Autorizzazione_DirittoRete.objects.filter(autorizzazione=autz)
		context['o365gruppi'] = Autorizzazione_O365Gruppo.objects.filter(autorizzazione=autz)
		context['nextcloud'] = Autorizzazione_NextCloud.objects.filter(autorizzazione=autz)
		context['porte'] = Autorizzazione_Porta.objects.filter(autorizzazione=autz)
		context['webapp'] = Autorizzazione_WebApp.objects.filter(autorizzazione=autz)
		context['gebevdiritti'] = Autorizzazione_GebevDiritto.objects.filter(autorizzazione=autz)
		context['gebevripartizioni'] = Autorizzazione_GebevRipartizione.objects.filter(autorizzazione=autz)
		context['web'] = Autorizzazione_Web.objects.filter(autorizzazione=autz)
		context['goffice2'] = Autorizzazione_GOffice2.objects.filter(autorizzazione=autz)
		
		
		self.download_name = self.base_name.format(
			uff = autz.ufficio.nome,
			data=autz.data,
			)
		return context
	
	