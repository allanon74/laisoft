# -*- coding: utf-8 -*-
from django.forms import ModelForm, BaseModelFormSet, modelformset_factory, Select, Form
from django.forms import SelectDateWidget, DateInput, NumberInput, TextInput, Textarea, EmailInput, HiddenInput, RadioSelect, ClearableFileInput, CheckboxSelectMultiple
from django.forms import ImageField, CharField, IntegerField, ChoiceField, SlugField, FileField
from django.contrib.gis.forms.widgets import OSMWidget
import django.contrib.gis.forms as gis_forms
from django.contrib.admin.widgets import AdminDateWidget
from .models import Tema, Segnalazione, si_no, Intervento, Team, Lavoro, Tipologia
from datetime import datetime
from .widgets import CustomDate, FilterSelect
from django.contrib.gis.forms import PointField

from .fotoform import FotoForm as _f

from django.utils import translation


from django.utils.translation import gettext_lazy as _


translation.activate('it')

#class MultipleFileInput(ClearableFileInput):
#	allow_multiple_selected = True

#class MultipleFileField(FileField):
#	def __init__(self, *args, **kwargs):
#		kwargs.setdefault("widget", MultipleFileInput())
#		super().__init__(*args, **kwargs)

#	def clean(self, data, initial=None):
#		single_file_clean = super().clean
#		if isinstance(data, (list, tuple)):
#			result = [single_file_clean(d, initial) for d in data]
#		else:
#			result = single_file_clean(data, initial)
#		return result

class SegnalazioneForm(ModelForm):
	template_name = "fr_jq_segnalazione.html"
	attrs = {
		"data-theme" : Tema.get_tema("Segnalazione")
		  }
	
	def __init__(self, *args, **kwargs):
		super(SegnalazioneForm, self).__init__(*args, **kwargs)
		self.fields['stato'].disabled = True
	
	class Meta:
		_tema = Tema.get_tema("Segnalazione")
		model = Segnalazione
		fields = [
			"oggetto",
			"descrizione",
			"tipo",
			"data_pianificazione", 
			"struttura",
			"stato",
			"origine",
			"segnalatore",
			"email",
			"telefono",
			"risposta",
			"id_documento",
			"periodico",
			"periodo",
			"cicli",
			"duplicare",
			"note",
			"eventi",
			]
		localized_fields = ['data_pianificazione',]
		widgets = {
			'oggetto' : TextInput(attrs={ "data-theme" : _tema,}, ), 
			'descrizione' : Textarea(attrs={ "data-theme" : _tema, }, ),
			"tipo" : Select(attrs={ "data-theme" : _tema,}, ),
			'data_pianificazione' : CustomDate(attrs={ "data-theme" : _tema, }, ),
			'struttura' : Select(attrs={ "data-theme" : _tema, }, ),
			'stato' : Select(attrs={ "data-theme" : _tema, }, ),
			'origine' : Select(attrs={ "data-theme" : _tema, }, ),
			'segnalatore' : TextInput(attrs={ "data-theme" : _tema, }, ),
			'email' : EmailInput(attrs={ "data-theme" : _tema, }, ),
			'telefono' : TextInput(attrs={ "data-theme" : _tema, }, ),
			'risposta' : Textarea(attrs={ "data-theme" : _tema, }, ),
			'id_documento' : TextInput(attrs={ "data-theme" : _tema, }, ),
			'periodico' : Select(choices= si_no, attrs={ "data-theme" : _tema, }, ),
			'periodo' : NumberInput(attrs={ "data-theme" : _tema, }, ),
			'cicli' : NumberInput(attrs={ "data-theme" : _tema, }, ),
			'duplicare' : Select(choices= si_no, attrs={ "data-theme" : _tema, }, ),
			'note' : Textarea(attrs={ "data-theme" : _tema, }, ),
			'eventi' : CheckboxSelectMultiple(attrs={ "data-theme" : _tema, }, )
			}
		
		
SegnalazioneFormset = modelformset_factory(Segnalazione, form=SegnalazioneForm)

class InterventoForm(ModelForm):
	template_name = "fr_jq_intervento.html"
	widget = {'attrs': {"data-theme" : Tema.get_tema("Intervento")}}
	
	def __init__(self, *args, **kwargs):
		super(InterventoForm, self).__init__(*args, **kwargs)
		self.fields['stato'].disabled = True
#		self.fields['segnalazione'].disabled = True
	
	class Meta:
		_tema = Tema.get_tema("Intervento")
		model = Intervento
		fields=[
			'segnalazione',
			"oggetto",
			"descrizione",
			"stato",
			"struttura",
			"priorita",
			"preposto",
			"precedente",
			"data_visibilita",
			"data_urgente",
			"data_esecuzione",
			"id_rabs",
			"periodico",
			"periodo",
			"cicli",
			"duplicare",
			"note",
			]
		widgets = {
#			'segnalazione' : FilterSelect(attrs={ "data-theme" : _tema, }),
			'segnalazione' :  HiddenInput(),
			'oggetto' : TextInput(attrs={ "data-theme" : _tema, }),
			'descrizione' : Textarea(attrs={ "data-theme" : _tema, }),
			'stato' : Select(attrs={ "data-theme" : _tema, }),
			'struttura' : Select(attrs={ "data-theme" : _tema, }),
			'priorita' : Select(attrs={ "data-theme" : _tema, }),
			'preposto' : Select(attrs={ "data-theme" : _tema, }),
			'precedente' : Select(attrs={ "data-theme" : _tema, }),
			'data_urgente' : CustomDate(attrs={ "data-theme" : _tema, }, ),
			'data_visibilita' : CustomDate(attrs={ "data-theme" : _tema, }, ), 
			'data_esecuzione' : CustomDate(attrs={ "data-theme" : _tema, }, ),
			'id_rabs' : TextInput(attrs={ "data-theme" : _tema, }),
			'periodico': Select(choices= si_no, attrs={ "data-theme" : _tema, }, ),
			'periodo' : NumberInput(attrs={ "data-theme" : _tema, }),
			'cicli' : NumberInput(attrs={ "data-theme" : _tema, }),
			'duplicare': Select(choices= si_no, attrs={ "data-theme" : _tema, }, ),
			'note' : Textarea(attrs={ "data-theme" : _tema, }),
			}

class InterventoNrForm(InterventoForm):
	template_name = "fr_jq_intervento_nr.html"

class TeamForm(ModelForm):
	template_name = "form_jq.html"
	widget = {'attrs': {"data-theme" : Tema.get_tema("Team")}}
	
	def __init__(self, *args, **kwargs):
		super(TeamForm, self).__init__(*args, **kwargs)
#		self.fields['intervento'].disabled = True
	
	class Meta:
		_tema = Tema.get_tema("Team")
		model = Team
		fields=[
			"intervento",
			"attivita",
			"tempo_stimato",
			"tempo_aumento",
			]
		widgets = {
#			'intervento' : FilterSelect(attrs={ "data-theme" : _tema, }),
			'intervento' :  HiddenInput(),
			'attivita': Select(attrs={ "data-theme" : _tema, }),
			'tempo_stimato': NumberInput(attrs={ "data-theme" : _tema, }),
			'tempo_aumento': NumberInput(attrs={ "data-theme" : _tema, }),
			}
		
class LavoroForm(ModelForm):
	template_name = "form_jq.html"
	widget = {'attrs': {"data-theme" : Tema.get_tema("Lavoro")}}

	def __init__(self, *args, **kwargs):
		super(LavoroForm, self).__init__(*args, **kwargs)
		self.fields['stato'].disabled = True
#		self.fields['team'].disabled = True
	
	class Meta:
		_tema = Tema.get_tema("lavoro")
		model = Lavoro
		fields=[
			"team",
			"oggetto",
			"descrizione",
			"stato",
			"collaboratore",
			"durata_prevista",
			"caposquadra",
			"accessorio",
			"urgenza",
			"mod_priorita",
			"note",
			]
		widgets = {
#			'team' : FilterSelect(attrs={ "data-theme" : _tema, }), 
			'team' : HiddenInput(),
			'oggetto' : TextInput(attrs={ "data-theme" : _tema, }),
			'descrizione' : Textarea(attrs={ "data-theme" : _tema, }),
			'stato' : Select(attrs={ "data-theme" : _tema, }),
			'collaboratore' : Select(attrs={ "data-theme" : _tema, }),
			'durata_prevista' : NumberInput(attrs={ "data-theme" : _tema, }),
			'caposquadra' : Select(attrs={ "data-theme" : _tema, }),
			'accessorio' : Select(choices=si_no, attrs={ "data-theme" : _tema, }),
			'urgenza' : Select(choices=si_no, attrs={ "data-theme" : _tema, }),
			'mod_priorita' : NumberInput(attrs={ "data-theme" : _tema, }),
			'note' : Textarea(attrs={ "data-theme" : _tema, }),
			}
		

class LavoroJqmForm(ModelForm):
	template_name = 'form_render.html'
	
	class Meta:
		_tema = Tema.get_tema("lavoro")
		model = Lavoro
		fields=[
			#"team__intervento__struttura",
			"oggetto",
			"descrizione",
			"note",
			]
		widgets = {
			'oggetto' : TextInput(attrs={ "data-theme" : _tema, }),
			'descrizione' : Textarea(attrs={ "data-theme" : _tema, }),
			'note' : Textarea(attrs={ "data-theme" : _tema, }),
			}
		

#class FotoForm(Form):
#	_tema = Tema.get_tema("tempilavoro")
#	foto = MultipleFileField(
#		required=True, 
#		label=_("Seleziona un'immagine"),
#		)
#	tipo = ChoiceField(
#		choices={t.id : t.nome_breve for t in Tipologia.foto()}, 
#		widget=Select(attrs={ "data-theme" : _tema, }),
#		required=True,
#		label = _("Tipologia di foto"),
#		)
#	posizione = PointField(
#		widget = OSMWidget(
#			attrs={
#				'map-width' : 300,
#				'map-heigth' : 200,
#				'template-name' : 'gis/openlayers-osm.html',
#				'default-lat': 57,
#				'default-lon' : 12
#				}
#			)
#		)
#	note = SlugField()
#	
#	class Meta:
#		fields = ['foto', 'tipo', 'posizione', ]
#		widgets=  {
#		#	'foto' : ClearableFileInput(attrs={'class': 'file-upload-input', 'id': 'file-selector',"multiple": True}),
#			'posizione' : OSMWidget(
#				attrs={
#					'map-width' : 300,
#					'map-heigth' : 200,
#					'template-name' : 'gis/openlayers-osm.html',
#					'default-lat': 57,
#					'default-lon' : 12
#					}
#				),
#			}
#		
		

class AllegatoForm(Form):
	_tema = Tema.get_tema("segnalazione")
	descrizione = CharField(
		required=True,
		strip=True,
		label= _("Descrizione")
						 )
	file = FileField(
	required=True, 
		label = _("Seleziona un allegato"),
	)
	
class FotoForm(_f):
	pass

class SegnalazioneStruttura(Form):
	_tema = Tema.get_tema('segnalazione')
	oggetto = CharField(
		required = True, 
		strip = True, 
		label = _("Oggetto"),
	)
	descrizione = CharField(
		required = True,
		strip = True, 
		label = _("Descrizione del problema"),		
	)
 
 
	class Meta:
			_tema = Tema.get_tema('segnalazione')
			widgets = {
				'oggetto' : TextInput(attrs={ "data-theme" : _tema, }),
				'descrizione' : Textarea(attrs={ "data-theme" : _tema, }),
			}