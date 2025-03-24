# -*- coding: utf-8 -*-
#from django.shortcuts import render
#from django.http import HttpResponse, FileResponse
from django_renderpdf.views import PDFView

from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

from .models import Formulario, Voto, Formulario_Obiettivo, Formulario_Prestazione, Formulario_Sociale, Formulario_Coordinamento, Firma
from .forms import ValutazioniFormSet

from dipendenti.models import Dipendente, Logo
from dipendenti.views import base_context
import datetime

#import os
#import io

#import dipendenti
#import valutazioni

#Import delle librerie per il PDF
#from reportlab.pdfgen import canvas
#from reportlab.lib import colors
#from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame, Image
#from reportlab.lib.styles import ParagraphStyle
#from reportlab.rl_config import defaultPageSize
#from reportlab.lib.units import mm
#from reportlab.pdfgen.canvas import Canvas
#from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
#Gestione font
#from reportlab.pdfbase import pdfmetrics
#from reportlab.pdfbase.ttfonts import TTFont


# Create your views here.

#PAGE_HEIGHT=defaultPageSize[1]
#PAGE_WIDTH=defaultPageSize[0]

PIX_WIDTH = 596
PIX_HEIGHT = 842

GRUPPO_ADMIN = "LS_valuzazioni_admin"
GRUPPO_DIRIGENTI = "LS_valutazioni_dirigenti"

def DataDipqualAnno_da(dipqual, anno):
	'''
		
	Parameters
	----------
	dipqual : tipo dipendnenti.models.dipendente_qualifica
		 il dipendente_qualifica su cui si applica l'anno 
		
		
	anno : integer
		l'anno su cui fare l'intersezione insiemistica 

	Returns
	-------
	data_in_anno_da: la data di inizio del periodo intersezione

	'''
	inizio = datetime.date(anno, 1, 1)
	return max(inizio, dipqual.data_da)

def DataDipqualAnno_a(dipqual, anno):
	'''
	

	Parameters
	----------
	dipqual : tipo dipendenti.models.dipendente_qualifica
		il dipendente_qualifica su cui si applica l'anno 
	anno : integer
		l'anno su cui fare l'intersezione insiemistica.

	Returns
	-------
	data_in_anno_a: la data di fine del periodo intersezione.

	'''
	fine = datetime.date(anno, 12, 31)
	if dipqual.data_a is None:
		return fine
	else:
		return min(dipqual.data_a, fine)
	
"""
def stampa_valutazione(request, id):
	# buffer per ricevere i dati PDF
	nome_file = "valutazione_{idogg}.pdf"
	buffer = io.BytesIO()
	
	# creazione dell'oggetto PDF utilizzando il buffer come "file"
	p = canvas.Canvas(buffer)
	
	txt = "Prova di stampa id: {idogg}"
	
	p.drawString(100,100, txt.format(idogg = id))
	
	p.showPage()
	p.save()
	
	buffer.seek(0)
	return FileResponse(buffer, as_attachment=True, filename=nome_file.format(idogg = id))

def stampa_griglia(request):
	# buffer per ricevere i dati PDF
	nome_file = "griglia.pdf"
	buffer = io.BytesIO()
	
	# creazione dell'oggetto PDF utilizzando il buffer come "file"
	p = canvas.Canvas(buffer)
	
	txt = "Prova di stampa: {idogg}"
	
	# p.drawString(100,100, txt.format(idogg = "griglia"))
	
	lw = 0.25
	col = colors.black
	
	for y in range(0,PIX_HEIGHT,10):
		
		if (y % 50) == 0:
			lw = 3.0
			col = colors.black
		else:
			lw = 0.25
			col = colors.lightgrey
			
		p.setLineWidth = lw
		p.setStrokeColor(col)
		p.line(0, y, PIX_WIDTH, y)
	
	lw = 0.25
	
	for x in range(0,PIX_WIDTH,10):
		
		if (x % 50) == 0:
			lw = 3.0
			col = colors.black
		else:
			lw = 0.25
			col = colors.lightgrey
			
		p.setLineWidth = lw
		p.setStrokeColor(col)
		p.line(x, 0, x, PIX_HEIGHT)
	
	p.showPage()
	p.save()
	
	buffer.seek(0)
	return FileResponse(buffer, as_attachment=True, filename=nome_file.format(idogg = id))

"""

"""
def Formulari(request):
	
	templ = 'formulari_test.html'
	context = base_context(request)
	
	formset = ValutazioniFormSet(request.POST, request.FILES)
	if formset.is_valid():
		formset.save()
		formset.save_m2m()
	else:
		formset = ValutazioniFormSet()
	
	context['formset'] = formset		
 	
	return render(request, templ, context)

"""


def DettaglioFormulario(request):
	loggeduser = None
	dipendente = None
	admin = False
	data_c = datetime.datetime(2020, 1, 1)
	
	to_do = request.POST.get('to_do', "none")
	
	templ = "formulario_firma.html"
	
	loggeduser = request.user

	if "_leifers" in loggeduser.username:
		dipendente = Dipendente.objects.get(userid=loggeduser.username)
	admin = loggeduser.groups.filter(name=GRUPPO_ADMIN).exists()
	
	id_formulario = request.POST['id_formulario']
	formul = Formulario.objects.get(id=id_formulario )
	if to_do == "firmato":
			frm = Firma(
				dipendente=dipendente, 
				formulario=formul, 
				data_firma=datetime.datetime.now, 
				note=request.POST.get('nota', ''),
				tipo_formulario=formul.tipo()
				)
			frm.save()
			
	firme_presenti = False
	firme = Firma.objects.filter(formulario=formul.id)
	if firme.count() >0:
		firme_presenti = True
	
	data_c = DataDipqualAnno_a(formul.dipqual, formul.anno.anno)
	
	context = base_context(request)
	
	context['firme_presenti'] = firme_presenti
	context['firme'] = firme
	context['admin'] = admin
	context['dipendente'] = dipendente
	context['loggeduser'] = loggeduser
	context['Formulario'] = formul
	context['qualifica'] = formul.dipqual.dipendente.qualifica_al(data_c)
	context['servizio'] = formul.dipqual.dipendente.servizio_al(data_c)
	context['ufficio'] = formul.dipqual.dipendente.ufficio_al(data_c)
	context['dirigente'] = formul.dipqual.dipendente.dirigente_al(data_c)
	context['responsabile'] = formul.dipqual.dipendente.responsabile_al(data_c)	
	context['Voto'] = Voto.objects.all().order_by('-valore')
	context['data_ass'] = formul.dipqual.dipendente.dipendente_dal()
	context['obiettivi'] = Formulario_Obiettivo.objects.filter(formulario=id_formulario )
	context['prestazioni'] = Formulario_Prestazione.objects.filter(formulario=id_formulario).order_by('prestazione__indice')
	context['sociali'] = Formulario_Sociale.objects.filter(formulario=id_formulario).order_by('sociale__indice')
	context['coordinamenti'] = Formulario_Coordinamento.objects.filter(formulario=id_formulario).order_by('coordinamento__indice')
	context['ruolo'] = formul.dipqual.dipendente.ruolo_al(data_c)
	
	val_tot = "-"
	tot = float(0)
	
	str_somma = "(Somma punti sezioni A + B + C)"
	str_somma_co = "(Somma punti sezioni A + B + C + D)"
	str_tot = "{totale:.2f}"
	
	if formul.media_a() is None or formul.media_b() is None or formul.media_c() is None:
		if formul.dipqual.dipendente.ruolo_al(data_c).responsabile == True:
			val_tot = str_somma_co
		else:
			val_tot = str_somma
	else:		
		if formul.dipqual.dipendente.ruolo_al(data_c).responsabile == True:
			if formul.media_d() is None:
				val_tot = str_somma_co
			else:
				tot = formul.media_a() + formul.media_b() + formul.media_c() + formul.media_d()
				val_tot = str_tot.format(totale = tot)
		else:
			tot = formul.media_a() + formul.media_b() + formul.media_c() 
			val_tot = str_tot.format(totale = tot)
	context['val_tot'] = val_tot
	
	return render(request, templ, context)


class Stampa(PDFView):
	template_name = 'base_pr.html'

class StampaFormulario(PDFView):
	template_name = 'formulario_pr.html'
	prompt_download = True
	download_name = "formulario.pdf"
	
	#queryset = Formulario.objects.filter(id=kwargs['id'])
	
	#it = Formulario.objects.get(id=kwargs['id'])
	
	def get_context_data(self, *args, **kwargs):
		formul = Formulario.objects.get(id=kwargs['id'], )
		
		data_c = DataDipqualAnno_a(formul.dipqual, formul.anno.anno)
		
		context = super().get_context_data(*args, **kwargs)
		context['Formulario'] = formul
		context['qualifica'] = formul.dipqual.dipendente.qualifica_al(data_c)
		context['servizio'] = formul.dipqual.dipendente.servizio_al(data_c)
		context['ufficio'] = formul.dipqual.dipendente.ufficio_al(data_c)
		context['dirigente'] = formul.dipqual.dipendente.dirigente_al(data_c)
#		context['prova'] = Formulario.objects.all()
#		context['gio'] = "giorgio bertoluzza"
		context['responsabile'] = formul.dipqual.dipendente.responsabile_al(data_c)
		context['Voto'] = Voto.objects.all().order_by('-valore')
		context['data_ass'] = formul.dipqual.dipendente.dipendente_dal()
		context['obiettivi'] = Formulario_Obiettivo.objects.filter(formulario=kwargs['id'])
		context['prestazioni'] = Formulario_Prestazione.objects.filter(formulario=kwargs['id']).order_by('prestazione__indice')
		context['sociali'] = Formulario_Sociale.objects.filter(formulario=kwargs['id']).order_by('sociale__indice')
		context['coordinamenti'] = Formulario_Coordinamento.objects.filter(formulario=kwargs['id']).order_by('coordinamento__indice')
		context['ruolo'] = formul.dipqual.dipendente.ruolo_al(data_c)
		
		val_tot = "-"
		tot = float(0)
		
		str_somma = "(Somma punti sezioni A + B + C)"
		str_somma_co = "(Somma punti sezioni A + B + C + D)"
		str_tot = "{totale:.2f}"
		
		if formul.media_a() is None or formul.media_b() is None or formul.media_c() is None:
			if formul.dipqual.dipendente.ruolo_al(data_c).responsabile == True:
				val_tot = str_somma_co
			else:
				val_tot = str_somma
		else:		
			if formul.dipqual.dipendente.ruolo_al(data_c).responsabile == True:
				if formul.media_d() is None:
					val_tot = str_somma_co
				else:
					tot = formul.media_a() + formul.media_b() + formul.media_c() + formul.media_d()
					val_tot = str_tot.format(totale = tot)
			else:
				tot = formul.media_a() + formul.media_b() + formul.media_c() 
				val_tot = str_tot.format(totale = tot)
		context['val_tot'] = val_tot
		
		desc = ""
		if formul.data_valutazione is None:
			desc = "Obiettivi"
		else:
			desc = "Valutazione"
		
		filename = "{cognome} {nome} ({matr}) - {dsc} anno {anno}.pdf"
		self.download_name = filename.format(
			cognome = formul.dipqual.dipendente.cognome, 
			nome = formul.dipqual.dipendente.nome, 
			matr = formul.dipqual.dipendente.matricola,
			dsc = desc,
			anno = formul.anno.anno
			)
		return context
	
class StampaFormularioDt(StampaFormulario):
	template_name = 'formulario_dt_pr.html'	
	
	str_somma = "(Summe Punkte A + B + C)"
	str_somma_co = "(Summe Punkte A + B + C + D)"
	str_tot = "{Total:.2f}"
		
#	def get(self, request):
#		return HttpResponse(self.render_to_response(self.get_context_data(), request))
	
#class FormularioView(ListView):
	
class Vista_abstract(LoginRequiredMixin, TemplateView):
	loggeduser = None
	dipendente = None
	admin = False


	
	class Meta:
		abstract = True
		
class VistaGriglia(Vista_abstract):
	template_name = "lista_valutazioni.html"
	
	
	def get(self, request, *args, **kwargs):
		self.loggeduser = request.user

		if "_leifers" in self.loggeduser.username:
			self.dipendente = Dipendente.objects.get(userid=self.loggeduser.username)
		self.admin = self.loggeduser.groups.filter(name=GRUPPO_DIRIGENTI).exists()
		return super().get(request, *args, **kwargs)
	
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['user'] = self.loggeduser
		context['dipendente'] = self.dipendente
		context['admin'] = self.admin
		context['logo'] = Logo.objects.get(id=1)
		
		context['formulari'] = Formulario.objects.filter(dipqual__dipendente = self.dipendente).order_by('-anno')

		
		
		return context
"""	
class VistaDettaglioFormulario(Vista_abstract):
	template_name = "formulario_firma.html"
	id_formulario = ""

	def get(self, request, *args, **kwargs):
		self.loggeduser = request.user

		if "_leifers" in self.loggeduser.username:
			self.dipendente = Dipendente.objects.get(userid=self.loggeduser.username)
		self.admin = self.loggeduser.groups.filter(name='ValutazioniAdmin').exists()
		self.id_formulario = request.POST['id_formulario']
		return super().get(request, *args, **kwargs)
	
	def get_context_data(self, **kwargs):
		formul = Formulario.objects.get(id=self.id_formulario )
		context = super().get_context_data(**kwargs)
		context['user'] = self.loggeduser
		context['dipendente'] = self.dipendente
		context['admin'] = self.admin
		
		context['Formulario'] = formul
#		context['prova'] = Formulario.objects.all()
#		context['gio'] = "giorgio bertoluzza"
		context['Voto'] = Voto.objects.all().order_by('-valore')
		context['data_ass'] = formul.dipqual.dipendente.dipendente_dal()
		context['obiettivi'] = Formulario_Obiettivo.objects.filter(formulario=kwargs['id'])
		context['prestazioni'] = Formulario_Prestazione.objects.filter(formulario=kwargs['id']).order_by('prestazione__indice')
		context['sociali'] = Formulario_Sociale.objects.filter(formulario=kwargs['id']).order_by('sociale__indice')
		context['coordinamenti'] = Formulario_Coordinamento.objects.filter(formulario=kwargs['id']).order_by('coordinamento__indice')
		context['ruolo'] = formul.dipqual.dipendente.ruolo_al()
		
		val_tot = "-"
		tot = float(0)
		
		str_somma = "(Somma punti sezioni A + B + C)"
		str_somma_co = "(Somma punti sezioni A + B + C + D)"
		str_tot = "{totale:.2f}"
		
		if formul.media_a() is None or formul.media_b() is None or formul.media_c() is None:
			if formul.dipqual.dipendente.ruolo_al().responsabile == True:
				val_tot = str_somma_co
			else:
				val_tot = str_somma
		else:		
			if formul.dipqual.dipendente.ruolo_al().responsabile == True:
				if formul.media_d() is None:
					val_tot = str_somma_co
				else:
					tot = formul.media_a() + formul.media_b() + formul.media_c() + formul.media_d()
					val_tot = str_tot.format(totale = tot)
			else:
				tot = formul.media_a() + formul.media_b() + formul.media_c() 
				val_tot = str_tot.format(totale = tot)
		context['val_tot'] = val_tot
		

		

		return context
	
	"""