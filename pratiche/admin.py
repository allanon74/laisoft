import random
import datetime
from django.db import models
from django.contrib import admin
from .models import GruppoPratica, Delega, Dipendente_GruppoPratica, TipoPratica, mail_test
from dipendenti.models import Dipendente
from django.utils.html import format_html
from django.forms import CheckboxSelectMultiple

BASE_URL = 'https://d3leifers.gvcc.net/dms/r/dd44bb51-c2d5-59d8-aba3-cedc1047c97c/o2/'

# Admin PRATICHE

# ------ CLASSI ASTRATTE ------

class Admin_abstract(admin.ModelAdmin):
	actions_on_top = True
	
	class Meta:
		abstract = True

class Multi_Inline_abstract(admin.TabularInline):
	extra = 1
	
	class Meta:
		abstract = True

# ------ AZIONI ------

@admin.action(description="segna le pratiche selezionate come completata")
def completa_pratica(modeladmin, request, queryset):
	queryset.update(completato=True, data_completamento = datetime.datetime.now())
	
@admin.action(description="Test invio e-mail")
def testmail(modeladmin, request, queryset):
	for delega in queryset:
		mail_test(delega.assegnatario.email, delega.gruppo.mittente, delega.documento, delega.url_pratica(), delega.gruppo.titolo_email, delega.gruppo.email)	

# ------ CLASSI INLINE ------

class Dipendente_GruppoPraticaInline(Multi_Inline_abstract):
	model = Dipendente_GruppoPratica
	formfield_overrides = {
		models.ManyToManyField: {'widget': CheckboxSelectMultiple},
	}

# ------ CLASSI ADMIN ------

class TipoPraticaAdmin(Admin_abstract):
	list_display = ['nome', ]
	search_fields = ('nome', )
#	inlines = (Dipendente_GruppoPraticaInline, )	

class GruppoPraticaAdmin(Admin_abstract):
	list_display = ['nome', 'responsabile', ]
	search_fields = ('nome', 'responsabile',)
	inlines = (Dipendente_GruppoPraticaInline, )
#	formfield_overrides = {
#		models.ManyToManyField: {'widget': CheckboxSelectMultiple},
#	}
	filter_horizontal = ['gestori', 'pratiche', ]

class DelegaAdmin(Admin_abstract):
	list_display = ['documento', 'peso', 'data_assegnazione', 'assegnatario','completato', 'url_d3one', ]
	search_fields = ('documento', 'assegnatario', )
	#readonly_fields = ['assegnatario', 'data_completamento', 'completato',]
	list_filter =['completato',]
	ordering = ['completato','-data_assegnazione']
	actions = [completa_pratica, testmail, ]
	
	fieldsets = (
		(None, {
			'fields': ('documento', 'richiedente', 'peso', 'tipo_pratica', 'pratica_collegata', 'gruppo', 'note',  )
		}),
		('Opzioni Avanzate', {
			'classes': ('collapse',),
			'fields': ('assegnatario', 'data_assegnazione', 'completato', 'data_completamento', 'system', 'origine', ),
		}),
	)
	
	def url_d3one(self, obj):
		txt = u'<a href="{}{}" target="_blank">documento</a>'
		return format_html(txt, BASE_URL, obj.documento)
	url_d3one.shortdescription = "D3 One"	

	def get_queryset(self, request):
		qs = super(DelegaAdmin, self).get_queryset(request)
		
		if request.user.is_superuser:
			return qs
		else:
			return qs.filter(system=False)
		
	def get_readonly_fields(self, request, obj=None):
		if request.user.is_staff:
			if request.user.is_superuser:
				return ['origine', 'data_assegnazione', ]
			else:
				return['assegnatario', 'data_completamento', 'completato','system', 'origine', 'data_assegnazione', ]
			
	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		dip = None
		grp = None
		
		if db_field.name == 'tipo_pratica':
			if request.user.is_superuser:
				pass
			elif "_leifers" in request.user.username:
				dip = Dipendente.objects.get(userid=request.user.username)
				grp = GruppoPratica.objects.filter(gestori__id__exact=dip.id)
				kwargs["queryset"] = TipoPratica.objects.filter(gruppopratica__in=grp).distinct()
			else:
				#Dip = request.user.dipendente
# 				uff = Ufficio.objects.filter(id__in = Ufficio_Dirigente.objects.filter(dirigente__exact=id_dip))
				#uff = Ufficio.objects.filter(dirigente__id=dip.id)
				#kwargs["queryset"] = Dipendente_Qualifica.objects.filter(dipendente__servizio__ufficio__in=uff)
				pass
				
		return super().formfield_for_foreignkey(db_field, request, **kwargs)	


# 	def save_model(self, request, obj, form, change):
# 		if obj.assegnatario is None or obj.assegnatario == "" :
# 			deleg = obj.gruppo.delegato.objects
# 			obj.assegnatario = random.choice(deleg)
# 		super().save_model(request, obj, form, change)


# ------ REGISTRAZIONI CLASSI ADMIN ------
#  admin.site.register(, Admin)
admin.site.register(GruppoPratica, GruppoPraticaAdmin)
admin.site.register(Delega, DelegaAdmin)
admin.site.register(TipoPratica, TipoPraticaAdmin)
