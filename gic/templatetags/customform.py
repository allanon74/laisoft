# -*- coding: utf-8 -*-
from django import template, forms
from gic.forms import SegnalazioneForm, InterventoForm, TeamForm, LavoroForm, LavoroJqmForm, InterventoNrForm, AllegatoForm
from gic.models import Tema, Segnalazione, Intervento, Team, Lavoro

register = template.Library()



@register.filter(name="form")
def form(value):
	if type(value) == Segnalazione:
		return SegnalazioneForm(instance=value)
	elif type(value) == Intervento:
		return InterventoForm(instance=value)
	elif type(value) == Team:
		return TeamForm(instance=value)
	elif type(value) == Lavoro:
		return LavoroForm(instance=value)
	else:
		form = forms.modelform_factory(type(value), fields="__all__")
		return form(instance=value)

@register.filter(name="form_allegato") 
def form_allegato(value):
	if type(value) == Segnalazione:
		return AllegatoForm()
	else:
		return None


@register.filter(name="form_nr")
def form_nr(value):
	if type(value) == Intervento:
		return InterventoNrForm(instance=value)
	else:
		return form(value)

@register.filter(name="jqform")
def jqform(value):
	if  type(value) == Lavoro:
		return LavoroJqmForm(instance=value)
	else:
		form = forms.modelform_factory(type(value), fields="__all__")
		return form(instance=value)

@register.filter(name="minuti")
def minuti(value):
	return (value % 3600) // 60

@register.filter(name="ore")
def ore(value):
	return value // 3600

@register.filter(name="secondi")
def secondi(value):
	return value % 60



@register.simple_tag(name="tema")
def tema(modello=""):
	return Tema.get_tema(modello)
	
"""	
	if modello == "segnalazione":
		return Tema.segnalazione()
	elif modello == "intervento":
		return Tema.intervento()
	elif modello == "team":
		return Tema.team()
	elif modello == "lavoro":
		return Tema.lavoro()
	elif modello == "salva":
		return Tema.salva()
	else:
		return "a"
	"""