import io, hashlib

from django.shortcuts import render, get_object_or_404, redirect 
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.template import loader
from django.urls import reverse 
import datetime

from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch, mm

PAGE_HEIGHT=defaultPageSize[1]
PAGE_WIDTH=defaultPageSize[0]
styles = getSampleStyleSheet()
Title = "Prontuario di Classificazione"
pageinfo = "Comune di Laives - Prontuario"



from .models import Tipo

def wiki(request):
	response = redirect('http://wikilaives/mediawiki/index.php/Pagina_principale')
	return response

def current_datetime(request):
	now = datetime.datetime.now()
	html = "<html><body>adesso sono le ore %s.</body></html>" % now
	return HttpResponse(html)

def elenco_tipi(completo=False):
	if completo:
		elenco = Tipo.objects.all().order_by('nome')
	else:
		elenco = elenco_tipi = Tipo.objects.filter(temporaneo=False).order_by('nome')
	
	return elenco

	
def index(request):
	template = loader.get_template('tabella/principale.html')
	context = {
		'elenco_tipi' : elenco_tipi(),
	}
	return HttpResponse(template.render(context, request))
	
def test(request):
	template = loader.get_template('tabella/test.html')
	context = {
		'elenco_tipi' : elenco_tipi(),
	}
	return HttpResponse(template.render(context, request))
	
def completo(request):
	template = loader.get_template('tabella/principale.html')
	context = {
		'elenco_tipi' : elenco_tipi(completo=True),
	}
	return HttpResponse(template.render(context, request))



def suggerimento(request):
	n_nome = request.POST.get('nome')
	n_nota =request.POST.get('nota')
	if n_nome == "" or n_nota == "" or n_nome is None or n_nota is None:
		messaggio = "Compilare i due campi"
	else:
		t = Tipo(nome=n_nome, nota=n_nota, temporaneo=True)
		t.save()
		messaggio = "Proposta %s inserita!" % n_nome
		n_nome = ""
		n_nota = ""

	template = loader.get_template('tabella/principale.html')
		
	context = {
		'messaggio' : messaggio,
		'nome' : n_nome,
		'nota' : n_nota,
		'elenco_tipi' : elenco_tipi(),
		}
		
	return HttpResponse(template.render(context, request))

	
def pdf(request):
	buffer = io.BytesIO()
	
	p = canvas.Canvas(buffer)
	p.setLineWidth(0)
	for x in range(0,600,10):
		if ((x % 50) == 0):
			p.setLineWidth(2)
		else:
			p.setLineWidth(0)
		p.line(x, 0, x, 850)
	for y in range(0,850,10):
		if ((y % 50) == 0):
			p.setLineWidth (2)
		else:
			p.setLineWidth(0)
		p.line(0, y, 600, y)
	
#		stringa = f"({x}, {y})"
#		p.drawString(x,y, stringa)
	p.showPage()
	p.save()
	
	buffer.seek(0)
	
	return FileResponse(buffer, as_attachment=True, filename='hello.pdf')
	
	
def pdfManual(request):
	buffer = io.BytesIO()
	#c = canvas.Canvas(buffer)
	#doc = SimpleDocTemplate("manuale.pdf")
	doc = SimpleDocTemplate(buffer)
	bgcol= colors.white
	Story = [Spacer(1, 2*inch)]
	style = styles["Normal"]
	styleNota = styles["Normal"]
	# for i in range(100):
		# bogustext = ("questo è il paragrafo numero %s.    " % i) *20
		# p = Paragraph(bogustext, style)
		# Story.append(p)
		# Story.append(Spacer(1, 0.2*inch))
	tabstyle = TableStyle([('GRID', (0,0), (-1,-1),0, colors.white),
							('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
							('FONTSIZE', (0,0), (0,0), 10),
							('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
							('FONTSIZE', (1,1), (-1,-1), 8), 
							('FONTNAME', (1,1), (-1,-1), 'Times-Roman'),
						])
	data = [["Tipo documento", "Classe di titolario", "Ufficio titolare", "Uffici in visibilità"],]
	riga = 1
	k = 0
	tipi = elenco_tipi(False)
	for tipo in tipi:
		s_vis = ""
		for vis in tipo.visibilita.all():
			s_vis += vis.id + " "
		n_titolari= ""
		n_classifica = ""
		if tipo.classifica is None:
			n_classifica = "-"
		else:
			n_classifica = tipo.classifica.id
		
		if tipo.titolari is None:
			n_titolari = "-" 
		else:
			n_titolari = tipo.titolari.id
		P0 = Paragraph('%s' % tipo.nome, style)
		P1 = Paragraph('%s' % n_classifica, style)
		P2 = Paragraph('%s' % n_titolari, style)
		P3 = Paragraph('%s' % s_vis, style)
		
		#data = [["%s" % tipo.nome, "%s" % tipo.classifica, "%s" % tipo.titolari, "%s" % s_vis ]]
		#data= [[P0, P1, P2, P3]]
		#t = Table(data, colWidths=[90.0*mm, 30.0*mm, 30.0*mm, 40.0*mm])
		#t= Table(data)
		#t.setStyle(tabstyle)
		#Story.append(t)
	
		#if tipo.nota == "" or tipo.nota is None:
			#Story.append(Spacer(1, 0.1*inch))
		#else:
			#Story.append(Spacer(1, 0.1*inch))
			#p=Paragraph("<para fontsize=6>%s</para>" %tipo.nota, style)
			#Story.append(p)
			#Story.append(Spacer(1, 0.1*inch))
			
		data += [[P0, P1, P2, P3],]
		riga +=1

		if tipo.nota == "" or tipo.nota is None:
		
			# per calcolare l'estensione delle colorazioni delle righe
			k = 0
		else:
			p=Paragraph("<para fontsize=6>%s</para>" %tipo.nota, styleNota)
			tabstyle.add('SPAN', (0, riga), (-1, riga))
			tabstyle.add('LEFTPADDING', (0, riga), (0, riga), 15)
			riga +=1
			data += [[p, "", "", ""],]
			k = 1
			
		tabstyle.add('BACKGROUND', (0, riga-1-k), (-1, riga-1), bgcol)
		if bgcol == colors.white:
			bgcol = colors.lightgrey
		else:
			bgcol = colors.white
		
	t= Table(data, colWidths=[90*mm, 30*mm, 30*mm, 50*mm], splitByRow=True, repeatRows=1)
	t.setStyle(tabstyle)
	Story.append(t)		
	
	doc.build(Story, onFirstPage=PrimaPagina, onLaterPages=PagineStandard)
	
	buffer.seek(0)
	
	return FileResponse(buffer, as_attachment=True, filename='manuale.pdf')
		
	
	
def PrimaPagina(canvas, doc):
	canvas.saveState()
	canvas.setFont('Times-Bold', 16)
	canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, Title)
	canvas.setFont('Times-Roman', 9)
	canvas.drawString(inch, 0.75 * inch, "Prima Pagina / %s" % pageinfo)
	canvas.restoreState
	
def PagineStandard(canvas, doc):
	canvas.saveState()
	canvas.setFont('Times-Roman', 9)
	canvas.drawString(inch, 0.75 * inch, "Pagina %d / %s" % (doc.page, pageinfo))
	canvas.restoreState	
	



	
# def uploadFile(request):
	# if request.method == 'POST':
		# form = UploadFileForm(request.POST, request.FILES)
		# if form.is_valid()
			# codice = calcola_hash(request.FILES['file'])
			# #return HttpResponseRedirect('/success/url/')
	# else:
		# form = UploadFileForm()
	# return render(request, 'upload.html', {'form': form})
	
