# -*- coding: utf-8 -*-
from django.forms import ModelForm, modelformset_factory
from .models import Formulario

class ValutazioniForm(ModelForm):
	
	class Meta:
		model = Formulario
		fields = "__all__"
		
ValutazioniFormSet = modelformset_factory(
	Formulario, 
	fields=['anno', 'dipqual', 'data_obiettivo', 'data_valutazione', 'obiettivi', 'prestazioni', 'sociali', 'coordinamenti']
	)
