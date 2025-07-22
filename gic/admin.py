from django.contrib import admin
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from django.utils.html import format_html
from django.forms import CheckboxSelectMultiple
from django.db import models
from django.contrib.gis.admin import GISModelAdmin

from django.utils.translation import gettext_lazy as _

from .models import ComplementaryColor
from .models import Mansione, Attivita, Priorita, Anno, Squadra, Tipologia, Collaboratore, CdC, Struttura, Diritto, Tema
from .models import Evento, Segnalazione, Intervento, Team, Foto, Lavoro, TempiLavoro, Allegato, Annotazione, Vista

from .models import CollaboratoreMansione, CollaboratoreAssenza, CollaboratoreReperibilita, EventoSegnalazione

from dipendenti.models import Servizio
# funzioni



# classi astratte

class Admin_a(GISModelAdmin):
	save_on_top = True
	list_display = ['id',]
	list_filter = []
	search_fields = []
	list_select_related = True
	ordering = ['-data_creazione',]
	readonly_fields = ['id', 'data_creazione', 'data_modifica', ]
	gis_widget_kwargs = {
		'attrs': {
			'map_width' : 400,
			'map_heigth' : 200,
			'template_name' : 'gis/openlayers-osm.html',
			'default_lat' : 46.42645,
			'default_lon' : 11.33852,
			'default_zoom' : 18,
			},
		}
	
	class Meta:
		abstract = True

class ItDe_a(TranslatableAdmin):
	list_display = ['nome_breve', 'color_square',]
	search_fields= [
		'translations__nome_breve',
		'translations__descrizione',
		]
	list_filter = []
	list_select_related = True
	#search_fields = []
	save_on_top = True
	ordering = ['-data_creazione',]
	readonly_fields = ['id', 'data_creazione', 'data_modifica', ]
	
	def color_square(self, obj):
		#txt = u'<div style="width:12px;heigth:12px;background-color:{};"></div>'
		txt = u'<p style="background-color:{};color:{};text-align:center;">{}</p>'
		return format_html(txt, obj.colore, obj.colore_testo(), obj.colore)
	color_square.short_description = _("Colore")
	
	class Meta:
		abstract = True
		
class Description_a(Admin_a):
	list_display = ['oggetto', 'id',]
	search_fields = [
		'oggetto',
		'descrizione',
		'note',
		]
	
class Inline_a(admin.TabularInline):
	extra = 1
	min_num = 0
	list_select_related = True
	readonly_fields = ['id', 'data_creazione', 'data_modifica', ]
	
	class Meta:
		abstract = True

class Stackline_a(admin.StackedInline):
	extra = 0
	min_num = 0
	list_select_related = True
	readonly_fields = ['id', 'data_creazione', 'data_modifica', ]
	
	class Meta:
		abstract = True
# classi inlines

class CollaboratoreMansioneInline(Inline_a):
	model = CollaboratoreMansione
	# radio_fields = {'mansione': admin.HORIZONTAL, }
	fields = ['collaboratore', 'mansione', 'data_da', 'data_a', ]
	
class CollaboratoreAssenzaInline(Inline_a):
	model = CollaboratoreAssenza
	# radio_fields = {'assenza': admin.HORIZONTAL, }
	fields = ['collaboratore', 'assenza', 'data_da', 'data_a', ]

class CollaboratoreReperibilitaInline(Inline_a):
	model = CollaboratoreReperibilita
	# radio_fields = {'reperibilita': admin.HORIZONTAL, }
	fields = ['collaboratore', 'reperibilita', 'data_da', 'data_a', ]

class EventoSegnalazioneInline(Inline_a):
	model = EventoSegnalazione
	
	
class SegnalazioneInterventoInline(Stackline_a):
	model = Intervento

	fieldsets = (
		(None, {
			'fields': ('oggetto', 'descrizione', 'priorita', 'preposto', 'struttura', 'stato', 'note', )
		}),
		('Dati di gestione', {
			'fields' : ('data_visibilita', 'data_urgente', 'data_esecuzione', 'precedente', 'segnalazione', 'id_rabs')
		}),
		("Periodica", {
#			'classes' : ('collapse', ),
			'fields' : ('periodico', 'periodo', 'cicli', 'duplicare',)
		}),
		('Avanzate', {
#			'classes': ('collapse', ),
			'fields': ('id', 'data_creazione', 'data_modifica',)
		}),
			)

class LavoroInline(Stackline_a):
	model = Lavoro

class TeamInline(Stackline_a):
	model = Team
	extra = 0
	min_num = 1
	inlines = [LavoroInline, ]
	
class FotoInline(Inline_a):
	model = Foto
	
class TempiLavoroInline(Inline_a):
	model=TempiLavoro

class AllegatoInline(Inline_a):
	model = Allegato
	
class AnnotazioneInline(Inline_a):
	model = Annotazione

class ServizioInline(Inline_a):
    model = Servizio
    	
# classi admin

class MansioneAdmin(ItDe_a):
	inlines = [CollaboratoreMansioneInline, ] 

class AttivitaAdmin(ItDe_a):
	filter_horizontal = ['mansioni', ]
	
class PrioritaAdmin(ItDe_a):
	ordering = ['valore',] + ItDe_a.ordering
	list_display = ItDe_a.list_display + ['valore', ]

	
class SquadraAdmin(ItDe_a):
	pass

class VistaAdmin(Admin_a):
	list_display = Admin_a.list_display + ["nome", "nome_modello", ]
	
class TipologiaAdmin(ItDe_a):
	list_display = ItDe_a.list_display + ['tipo', 'abbreviazione', 'ordine', 'fa_icon' ]
	list_filter = ItDe_a.list_filter + ['tipo', ]
	list_editable = ['ordine', 'fa_icon',]
	ordering = ['tipo', 'ordine','abbreviazione', ] 
	
class CollaboratoreAdmin(Admin_a):
	list_display = ['dipendente', 'squadra', 'sigla', 'vista', ] + Admin_a.list_display
	list_editable = ['vista',]
	radio_fields = {'squadra': admin.HORIZONTAL, }
	autocomplete_fields = ['dipendente',]
	inlines = [CollaboratoreMansioneInline, CollaboratoreAssenzaInline, CollaboratoreReperibilitaInline]
	search_fields = ['dipendente__cognome', 'dipendente__nome', ]
	
class CdCAdmin(ItDe_a):
	pass
	
class StrutturaAdmin(ItDe_a):
	# search_fields = ['translations__nome_breve', 'translations__descrizione',]
	# ordering = ['nome_breve', ]
	# inlines = [ServizioInline, ]
	filter_horizontal = ['autorizzati', ]

class EventoAdmin(ItDe_a):
	inlines = [EventoSegnalazioneInline, ]

class SegnalazioneAdmin(Description_a):
	radio_fields = {'origine': admin.VERTICAL, 'tipo' : admin.VERTICAL, 'stato' : admin.VERTICAL}
	fieldsets = (
		(None, {
			'fields': ('oggetto', 'descrizione', 'tipo', 'data_pianificazione', 'struttura', 'stato', 'tags', 'note', )
		}),
		('Dati della Segnalazione', {
			'fields' : ('origine', 'segnalatore', 'email', 'telefono', 'risposta', 'id_documento', )
		}),
		("Periodica", {
#			'classes' : ('collapse', ),
			'fields' : ('periodico', 'periodo', 'cicli', 'duplicare',)
		}),
		('Avanzate', {
#			'classes': ('collapse', ),
			'fields': ('id', 'data_creazione', 'data_modifica',)
		}),
		)
	inlines = [SegnalazioneInterventoInline, 
			AllegatoInline,
#			EventoSegnalazioneInline
			]
	formfield_overrides = {
		models.ManyToManyField: {'widget' : CheckboxSelectMultiple},
		}
	search_fields = ['oggetto', 'descrizione']
	autocomplete_fields = ['struttura', ]

class InterventoAdmin(Description_a):
	fieldsets = SegnalazioneInterventoInline.fieldsets
	inlines = (TeamInline, FotoInline, )
	autocomplete_fields = ['preposto', 'struttura', ]
	radio_fields ={'priorita' : admin.HORIZONTAL, 'stato' : admin.HORIZONTAL}
	search_fields = ['oggetto', 'descrizione']
	
class TeamAdmin(Admin_a):
	inlines = [LavoroInline, ]
	list_display = ['intervento', 'attivita', 'tempo_aumento', ] + Admin_a.list_display
	list_editable = ['tempo_aumento', ]
	search_fields = ['intervento__oggetto', 'intervento__descrizione', ]

class FotoAdmin(Admin_a):
	pass

class LavoroAdmin(Description_a):
	inlines = [TempiLavoroInline, AnnotazioneInline, ]
	autocomplete_fields = ['collaboratore', 'caposquadra']
	list_display = ['oggetto', 'collaboratore', 'mod_priorita', 'val_priorita',]
	list_filter = ['collaboratore', ]
	list_editable = ['collaboratore', 'mod_priorita', ]

class TempiLavoroAdmin(Admin_a):
	model = TempiLavoro
	list_display = ['lavoro', 'get_collaboratore', 'inizio', 'fine', ] + Admin_a.list_display
	list_filter = Admin_a.list_filter + ['lavoro__collaboratore',]
	
	@admin.display(description = "Collaboratore", ordering = "lavoro__collaboratore")
	def get_collaboratore(self, obj):
		return obj.lavoro.collaboratore
	
class AllegatoAdmin(Admin_a):
	list_display = ['segnalazione', 'file', ] + Admin_a.list_display
	
class AnnotazioneAdmin(Admin_a):
	list_display = ['lavoro', ] + Admin_a.list_display
	
class DirittoAdmin(Admin_a):
	list_display = ['nome', 'capocantiere', 'caposquadra', 'operaio', 'ufficio', 'struttura', 'coordinatore',]
	list_editable = ['capocantiere', 'caposquadra', 'operaio', 'ufficio', 'struttura', 'coordinatore',]
	
class TemaAdmin(Admin_a):
	list_display = ['modello', 'tema',]
	list_editable = ['tema',]

# registrazioni
# admin.site.register(, )
admin.site.register(Mansione, MansioneAdmin)
admin.site.register(Attivita, AttivitaAdmin)
admin.site.register(Priorita, PrioritaAdmin)
#admin.site.register(Anno, AnnoAdmin)
admin.site.register(Squadra, SquadraAdmin)
admin.site.register(Tipologia, TipologiaAdmin)
admin.site.register(Collaboratore, CollaboratoreAdmin)
admin.site.register(CdC, CdCAdmin)
admin.site.register(Struttura, StrutturaAdmin)
admin.site.register(Evento, EventoAdmin)
admin.site.register(Segnalazione, SegnalazioneAdmin)
admin.site.register(Intervento, InterventoAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Foto, FotoAdmin)
admin.site.register(Lavoro, LavoroAdmin)
admin.site.register(TempiLavoro, TempiLavoroAdmin)
admin.site.register(Allegato, AllegatoAdmin)
admin.site.register(Annotazione, AnnotazioneAdmin)
admin.site.register(Diritto, DirittoAdmin)
admin.site.register(Tema, TemaAdmin)
admin.site.register(Vista, VistaAdmin)
