from django.contrib import admin, auth
from .models import *
from .views import StampaFormulario, StampaFormularioDt
from dipendenti.models import Dipendente, Ufficio, Dipendente_Qualifica, Servizio
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin

from valutazioni.models import Anno, Voto, TipoValutazione, Elemento, Formulario, CategoriaElementi, Firma, Formulario_Obiettivo, Formulario_Prestazione, Formulario_Sociale, Formulario_Coordinamento 

# Admin VALUTAZIONI

BASE_URL="https://laisoft.gvcc.net/valutazioni/"

# ------ CLASSI ASTRATTE ------

class Admin_abstract(admin.ModelAdmin):
	actions_on_top = True
	
	class Meta:
		abstract = True
		

class Multi_Inline_abstract(admin.TabularInline):
	extra = 1
	
	class Meta:
		abstract = True 

# ------ CLASSI INLINE ------

class Formulario_ObiettivoInline(Multi_Inline_abstract):
	model = Formulario_Obiettivo
	min_num = 1
	extra = 0
	
class Formulario_PrestazioneInline(Multi_Inline_abstract):
	model = Formulario_Prestazione
	#extra = 7
	min_num = 7
	max_num = 7

class Formulario_SocialeInline(Multi_Inline_abstract):
	model = Formulario_Sociale
	#extra = 3
	min_num = 3
	max_num = 3

class Formulario_CoordinamentoInline(Multi_Inline_abstract):
	model = Formulario_Coordinamento
	extra = 2
	max_num = 2


class Formulario_FirmaInline(Multi_Inline_abstract):
	model = Firma
	extra = 0
	min_num = 0 
	readonly_fields = ['dipendente', 'formulario', 'note', 'tipo_formulario', ]
	

# ------ AZIONI ------

#@admin.action(description="Stampa le valutazioni selezionate.")
#def stampa_valutazione(modeladmin, request, queryset):
#	for val in queryset:
#		response = HttpResponse()

# ------ CLASSI ADMIN ------

class AnnoAdmin(Admin_abstract):
	list_display =('id', 'anno', )
	search_fields = ['anno', ]

class VotoAdmin(Admin_abstract):
	list_display = ('valore', 'descrizione_it', 'descrizione_td', )
	search_fields = ['valore', 'descrizione_it', 'descrizione_td', ]
	
class TipoValutazioneAdmin(Admin_abstract):
	list_display = ('nome', 'descrizione_it', 'sezione', )
	search_fields = ('nome', 'descrizione_it', )
	
class ElementoAdmin(Admin_abstract):
	list_display = ('descrizione_it', 'tipo_valutazione', 'categoria',  )
	list_editable = ('categoria', )
	search_fields = ['descrizione_it', ]
	list_filter = ('tipo_valutazione__nome', )
	

class FormularioAdmin(SimpleHistoryAdmin):
	list_display = ('anno', 'dipqual', 'tipo', 'url_italiano', 'url_tedesco', )
	list_filter = ('anno', 'dipqual__dipendente__servizio', )
	history_list_display = ["status",]
	inlines = (Formulario_ObiettivoInline, Formulario_PrestazioneInline, Formulario_SocialeInline, Formulario_CoordinamentoInline, Formulario_FirmaInline,)
	
	fieldsets = (
		(None, {
			'fields': ('anno', 'dipqual', 'data_obiettivo', 'data_valutazione', 'note', )
		}),
		('Layout', {
			'classes': ('collapse', ),
			'fields': ('logo',  )
		}),
	)

	def url_tedesco(self, obj):
		txt = u"<a href={}stampaformularioted/{}/>Stampa in tedesco</a>"
		return format_html(txt, BASE_URL, obj.id)
	url_tedesco.short_description = "Tedesco"

	def url_italiano(self, obj):
		txt = u"<a href={}stampaformulario/{}/>Stampa in italiano</a>"
		return format_html(txt, BASE_URL, obj.id)
	url_italiano.short_description = "Italiano"

	def tipo(self, obj):
		desc = ""
		if obj.data_valutazione is None:
			desc = "Obiettivi"
		else:
			desc = "Valutazione"
		return desc
           
	def get_queryset(self, request):
		dip = None
		#uff = None
		ser = None
		qs = super(FormularioAdmin, self).get_queryset(request)
		if request.user.is_superuser:
			return qs
		if "_leifers" in request.user.username:
			dip = Dipendente.objects.get(userid=request.user.username)
		else:
			dip = request.user.dipendente
#		if dip.ruolo_al().segretario == True or dip.ruolo_al().ammsistema == True:
		if dip.ruolo_al().ammsistema == True:
			return qs
		else:

			#uff = Ufficio.objects.filter(dirigente__id=dip.id)
			#return qs.filter(dipqual__dipendente__servizio__ufficio__in=uff)
			
			ser = Servizio.objects.filter(responsabile__id=dip.id)
			return qs.filter(dipqual__dipendente__servizio__in=ser).distinct()
	
	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		dip = None
		#uff = None
		ser = None
		if db_field.name == 'dipqual':
			if request.user.is_superuser:
				pass
			elif "_leifers" in request.user.username:
				dip = Dipendente.objects.get(userid=request.user.username)

				#uff = Ufficio.objects.filter(dirigente__id=dip.id)
				#kwargs["queryset"] = Dipendente_Qualifica.objects.filter(dipendente__servizio__ufficio__in=uff).distinct()
				ser = Servizio.objects.filter(responsabile__id=dip.id)
				kwargs["queryset"] = Dipendente_Qualifica.objects.filter(dipendente__servizio__in=ser).distinct()
			else:
				dip = request.user.dipendente

				#uff = Ufficio.objects.filter(dirigente__id=dip.id)
				#kwargs["queryset"] = Dipendente_Qualifica.objects.filter(dipendente__servizio__ufficio__in=uff).distinct()				
				ser = Servizio.objects.filter(responsabile__id=dip.id)
				kwargs["queryset"] = Dipendente_Qualifica.objects.filter(dipendente__servizio__in=ser).distinct()											  
															 
															 

		return super().formfield_for_foreignkey(db_field, request, **kwargs)
		
class CategoriaElementiAdmin(Admin_abstract):
	list_display = ('descrizione_it', 'indice', )
	search_fields = ['descrizione_it', ]


class FormularioHistoryAdmin(SimpleHistoryAdmin):
	list_display = ["id", 'name', 'status',]
	history_list_display = ["status"]
	search_fields = ['name', 'user__username',]

# ------ REGISTRAZIONI CLASSI ADMIN ------
	
admin.site.register(Anno, AnnoAdmin)
admin.site.register(Voto, VotoAdmin)
admin.site.register(TipoValutazione, TipoValutazioneAdmin)
admin.site.register(Elemento, ElementoAdmin)
admin.site.register(Formulario, FormularioAdmin)
admin.site.register(CategoriaElementi, CategoriaElementiAdmin)
#admin.site.register(Formulario, FormularioHistoryAdmin)
#admin.site.register(Firma)


#admin.site.register(, Admin)