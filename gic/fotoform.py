# -*- coding: utf-8 -*-
from django.forms import Select, Form
from django.forms import ClearableFileInput
from django.forms import ChoiceField, FileField, SlugField
from django.contrib.gis.forms.widgets import OSMWidget

from .models import Tema, Tipologia

from django.contrib.gis.forms import PointField

from django.utils import translation


from django.utils.translation import gettext_lazy as _


translation.activate('it')

class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result



class FotoForm(Form):
	_tema = Tema.get_tema("tempilavoro")
	foto = MultipleFileField(
		required=True, 
		label=_("Seleziona un'immagine"),
		)
	tipo = ChoiceField(
		choices={t.id : t.nome_breve for t in Tipologia.foto()}, 
		widget=Select(attrs={ "data-theme" : _tema, }),
		required=True,
		label = _("Tipologia di foto"),
		)
	note = SlugField()
	posizione = PointField(
		widget = OSMWidget(
			attrs={
				'map_width' : 400,
				'map_heigth' : 200,
				'template_name' : 'gis/openlayers-osm.html',
				'default_lat': 46.42645,
				'default_lon' : 11.33852,
				'default_zoom' : 18
				}
			)
		)

	
	class Meta:
		fields = ['foto', 'tipo', 'posizione', ]
		widgets=  {
		#	'foto' : ClearableFileInput(attrs={'class': 'file-upload-input', 'id': 'file-selector',"multiple": True}),
			'posizione' : OSMWidget(
				attrs={
					'map_width' : 400,
					'map_heigth' : 200,
					'template_name' : 'gis/openlayers-osm.html',
					'default_lat' : 46.42645,
					'default_lon' : 11.33852,
					'default_zoom' : 18
					}
				),
			}
		
		
