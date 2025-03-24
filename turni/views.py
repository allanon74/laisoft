import io, hashlib, datetime

from django.shortcuts import render, get_object_or_404, redirect 
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.template import loader
from django.urls import reverse 

from .models import Turno, Giorno, Ruolo, Fascia, Persona

# Create your views here.
def tabella_turni_test(request):
	template = loader.get_template('prova.html')
	dt = datetime.datetime.now()	
	turni = Turno.objects.filter(giorno__data__gt=dt).order_by('giorno__data', 'fascia', 'ruolo')
	giorni = Giorno.objects.filter(data__gte=dt)
	ruoli = Ruolo.objects.all()
	fasce = Fascia.objects.all()
	
	pt_turni = {}
	fsc_a = ''
	rlo_a = ''
	grn_a = dt
	persone = ''
	nome = ''
	stile = ""
	
	for trn in turni:
		nome = trn.persona.nome_completo()
					
		if trn.confermato:
			stile = ' style="font-weight:bold;"'
		elif trn.avvisato:
			stile = ' style="color:blue;"'
		else:
			stile = ' style="font-style:italic;color:red;"'

		nome = '<p%s>%s</p>' % (stile, nome)
		
				
		
		if trn.giorno.data == grn_a and trn.ruolo.nome == rlo_a and trn.fascia.nome == fsc_a:
			persone += nome
		else:
			persone = nome
		
		
		
		pt_turni.setdefault('%s<br />%s' % (trn.giorno.data_giorno(), trn.fascia.desc_breve), {}).update({trn.ruolo.nome: persone})
	
		fsc_a = trn.fascia.nome
		rlo_a = trn.ruolo.nome
		grn_a = trn.giorno.data
		
	context = {
		'elenco_turni' : pt_turni,
		'elenco_ruoli' : ruoli,
	}
	return HttpResponse(template.render(context, request))

	
def tabella_turni(request):
	template = loader.get_template('tabella.html')
	dt = datetime.datetime.now()	
	turni = Turno.objects.filter(giorno__data__gte=dt).order_by('giorno__data', 'fascia__ordine', 'ruolo')
	giorni = Giorno.objects.filter(data__gte=dt)
	ruoli = Ruolo.objects.all()
	fasce = Fascia.objects.all()
	
	pt_turni = {}
	fsc_a = ''
	rlo_a = ''
	grn_a = dt
	persone = ''
	nome = ''
	stile = ""
	
	for trn in turni:
		nome = trn.persona.nome_completo()
					
		if trn.confermato:
			stile = ' style="font-weight:bold;"'
		elif trn.avvisato:
			stile = ' style="color:blue;"'
		else:
			stile = ' style="font-style:italic;color:red;"'

		nome = '<p%s>%s</p>' % (stile, nome)
		
				
		
		if trn.giorno.data == grn_a and trn.ruolo.nome == rlo_a and trn.fascia.nome == fsc_a:
			persone += nome
		else:
			persone = nome
		
		
		
		pt_turni.setdefault('%s<br />%s' % (trn.giorno.data_giorno(), trn.fascia.desc_breve), {}).update({trn.ruolo.nome: persone})
		pt_turni.setdefault('%s<br />%s' % (trn.giorno.data_giorno(), trn.fascia.desc_breve), {}).update({'giorno': trn.giorno.data})
		pt_turni.setdefault('%s<br />%s' % (trn.giorno.data_giorno(), trn.fascia.desc_breve), {}).update({'fascia': trn.fascia})
		
		
		fsc_a = trn.fascia.nome
		rlo_a = trn.ruolo.nome
		grn_a = trn.giorno.data
		
	context = {
		'elenco_turni' : pt_turni,
		'elenco_ruoli' : ruoli,
	}
	return HttpResponse(template.render(context, request))	

	
def tabella_turni_semplice(request):
	template = loader.get_template('prova_turni.html')
	dt = datetime.datetime.now()	
	turni = Turno.objects.filter(giorno__data__gte=dt).order_by('giorno__data', 'fascia', 'ruolo')
	ruoli = Ruolo.objects.all()
	
		
	context = {
		'elenco_turni' : turni,
		'elenco_ruoli' : ruoli,
	}
	return HttpResponse(template.render(context, request))	

def tabella_giorno(request, aa, mm, gg):
	template = loader.get_template('giorno.html')
	sel_data = datetime.datetime(aa, mm, gg)
	sel_giorno = Giorno.objects.get(data=seldata)
		
	context = {
		'elenco_turni' : Turno.objects.filter(giorno=sel_giorno),
	}
	
	return HttpResponse(template.render(context, request))
	
