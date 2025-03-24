from django.contrib import admin
from django.forms import CheckboxSelectMultiple
from django.db import models
from django.utils.html import format_html
from django.conf import settings

from laisoft.admin import AdminWithSelectRelated, AdminInlineWithSelectRelated, FilterWithSelectRelated

from .models import TipoGenerico, AmbitiPassword, TestoFisso, Share, Atto, Password, Designazione, Capoverso, Autorizzazione, Template
from .models import GruppoSamba, SGVCanale, GOffice, D3Diritto, Generico, DirittoRete, O365Gruppo, NextCloud, Porta, WebApp, GebevDiritto, GebevRipartizione, Web, D3Gruppo, GOffice2
from .models import Atto_GruppoSamba, Atto_SGVCanale, Atto_GOffice, Atto_D3Diritto, Atto_Generico, Atto_DirittoRete, Atto_D3Gruppo
from .models import Atto_O365Gruppo, Atto_NextCloud, Atto_Porta, Atto_WebApp, Atto_GebevDiritto, Atto_GebevRipartizione, Atto_Web, Atto_GOffice2

from .models import Autorizzazione_GruppoSamba, Autorizzazione_SGVCanale, Autorizzazione_GOffice, Autorizzazione_D3Diritto, Autorizzazione_Generico, Autorizzazione_DirittoRete, Autorizzazione_D3Gruppo
from .models import Autorizzazione_O365Gruppo, Autorizzazione_NextCloud, Autorizzazione_Porta, Autorizzazione_WebApp, Autorizzazione_GebevDiritto, Autorizzazione_GebevRipartizione, Autorizzazione_Web, Autorizzazione_GOffice2

from .models import Template_GruppoSamba, Template_SGVCanale, Template_GOffice, Template_D3Diritto, Template_Generico, Template_DirittoRete, Template_D3Gruppo
from .models import Template_O365Gruppo, Template_NextCloud, Template_Porta, Template_WebApp, Template_GebevDiritto, Template_GebevRipartizione, Template_Web, Template_GOffice2



# BASE_URL="http://leifersasdjango.leifers.gvcc.net/accessi/"

BASE_URL = "{base}accessi/".format(base=settings.BASE_URL)

# Modelli astratti

class Multi_Inline_abstract(admin.TabularInline):
	#ordering = ('nome',)
	extra = 0
	min_num = 0
	
	class Meta:
		abstract = True

class admin_abstract(admin.ModelAdmin):
	save_on_top = True
	
	class Meta:
		abstract = True	

		
class DirittoAdmin(admin_abstract):
	list_display = ('id', 'nome', 'nome_it', 'nome_de', 'descrizione', 'attivo',)
	search_fields = ['nome', 'nome_it', 'nome_de', 'descrizione', 'descrizione_de',]
	list_editable = ['attivo', 'nome', 'nome_it', 'nome_de', 'descrizione', ]

	
		
class Diritti_inline_abstract(AdminInlineWithSelectRelated):
	extra = 0
	min_num = 0
	readonly_fields = ['data_inserimento', 'data_modifica', 'data_disattivazione', 'utente_inserimento', 'utente_modifica', 'utente_disattivazione', 'utente_admin']
	#raw_id_fields = ("diritto", )
	autocomplete_fields = ["diritto", ]
	list_select_related = ['diritto', ]
	
	class Meta:
		abstract = True
		
	def save_model (self, request, obj, form, change):
		if not change:
			obj.utente_inserimento = request.user
		else:
			if 'diritto_attivato' in form.changed_data:
					obj.utente_admin = request.user
		obj.utente_modifica = request.user
		

		super().save_model(request, obj, form, change)	
		
# Modelli Inline

class PasswordInline(admin.StackedInline):
	model = Password
	#filter_horizontal = ['ambiti', ]
	radio_fields = {'testo': admin.VERTICAL}
	
	def formfield_for_manytomany(self, db_field, request=None, **kwargs):
		if db_field.name == 'ambiti':
			kwargs['widget'] = CheckboxSelectMultiple()
			kwargs['help_text'] = ''
		
		return db_field.formfield(**kwargs)

class CapoversoInline(Multi_Inline_abstract):
	model=Capoverso

class DesignazioneInline(admin.StackedInline):
	model = Designazione
	radio_fields = {'testo': admin.VERTICAL}

class GruppoSamba_ShareInline(Multi_Inline_abstract):
	model = Share

# Classi inline autorizzazioni



class GruppoSambaInline(Diritti_inline_abstract):
	model = Atto_GruppoSamba
	#raw_id_fields = ("diritto", )

class a_GruppoSambaInline(Diritti_inline_abstract):
	model = Autorizzazione_GruppoSamba
	#raw_id_fields = ("diritto", )

class t_GruppoSambaInline(Diritti_inline_abstract):
	model = Template_GruppoSamba
	#raw_id_fields = ("diritto", )


class SGVCanaleInline(Diritti_inline_abstract):
	model = Atto_SGVCanale
	#raw_id_fields = ("diritto", )

class a_SGVCanaleInline(Diritti_inline_abstract):
	model = Autorizzazione_SGVCanale
	#raw_id_fields = ("diritto", )

class t_SGVCanaleInline(Diritti_inline_abstract):
	model = Template_SGVCanale
	#raw_id_fields = ("diritto", )


class GOfficeInline(Diritti_inline_abstract):
	model = Atto_GOffice
	#raw_id_fields = ("diritto", )

class a_GOfficeInline(Diritti_inline_abstract):
	model = Autorizzazione_GOffice
	#raw_id_fields = ("diritto", )

class t_GOfficeInline(Diritti_inline_abstract):
	model = Template_GOffice
	#raw_id_fields = ("diritto", )


class D3GruppoInline(Diritti_inline_abstract):
	model = Atto_D3Gruppo
	#raw_id_fields = ("diritto", )

class a_D3GruppoInline(Diritti_inline_abstract):
	model = Autorizzazione_D3Gruppo
	#raw_id_fields = ("diritto", )

class t_D3GruppoInline(Diritti_inline_abstract):
	model = Template_D3Gruppo
	#raw_id_fields = ("diritto", )


class D3DirittoInline(Diritti_inline_abstract):
	model = Atto_D3Diritto
	#raw_id_fields = ("diritto", )

class a_D3DirittoInline(Diritti_inline_abstract):
	model = Autorizzazione_D3Diritto
	#raw_id_fields = ("diritto", )

class t_D3DirittoInline(Diritti_inline_abstract):
	model = Template_D3Diritto
	#raw_id_fields = ("diritto", )


class GenericoInline(Diritti_inline_abstract):
	model = Atto_Generico
	#raw_id_fields = ("diritto", )

class a_GenericoInline(Diritti_inline_abstract):
	model = Autorizzazione_Generico
	#raw_id_fields = ("diritto", )

class t_GenericoInline(Diritti_inline_abstract):
	model = Template_Generico
	#raw_id_fields = ("diritto", )


class DirittoReteInline(Diritti_inline_abstract):
	model = Atto_DirittoRete
	#raw_id_fields = ("diritto", )

class a_DirittoReteInline(Diritti_inline_abstract):
	model = Autorizzazione_DirittoRete
	#raw_id_fields = ("diritto", )

class t_DirittoReteInline(Diritti_inline_abstract):
	model = Template_DirittoRete
	#raw_id_fields = ("diritto", )


class O365GruppoInline(Diritti_inline_abstract):
	model = Atto_O365Gruppo
	#raw_id_fields = ("diritto", )

class a_O365GruppoInline(Diritti_inline_abstract):
	model = Autorizzazione_O365Gruppo
	#raw_id_fields = ("diritto", )

class t_O365GruppoInline(Diritti_inline_abstract):
	model = Template_O365Gruppo
	#raw_id_fields = ("diritto", )


class NextCloudInline(Diritti_inline_abstract):
	model = Atto_NextCloud
	#raw_id_fields = ("diritto", )

class a_NextCloudInline(Diritti_inline_abstract):
	model = Autorizzazione_NextCloud
	#raw_id_fields = ("diritto", )

class t_NextCloudInline(Diritti_inline_abstract):
	model = Template_NextCloud
	#raw_id_fields = ("diritto", )


class PortaInline(Diritti_inline_abstract):
	model = Atto_Porta 
	#raw_id_fields = ("diritto", )

class a_PortaInline(Diritti_inline_abstract):
	model = Autorizzazione_Porta 
	raw_id_fields = ("diritto", )

class t_PortaInline(Diritti_inline_abstract):
	model = Template_Porta 
	#raw_id_fields = ("diritto", )


class WebAppInline(Diritti_inline_abstract):
	model = Atto_WebApp
	raw_id_fields = ("diritto", )

class a_WebAppInline(Diritti_inline_abstract):
	model = Autorizzazione_WebApp
	#raw_id_fields = ("diritto", )

class t_WebAppInline(Diritti_inline_abstract):
	model = Template_WebApp
	raw_id_fields = ("diritto", )


class GebevDirittoInline(Diritti_inline_abstract):
	model = Atto_GebevDiritto
	#raw_id_fields = ("diritto", )

class a_GebevDirittoInline(Diritti_inline_abstract):
	model = Autorizzazione_GebevDiritto
	#raw_id_fields = ("diritto", )

class t_GebevDirittoInline(Diritti_inline_abstract):
	model = Template_GebevDiritto
	#raw_id_fields = ("diritto", )


class GebevRipartizioneInline(Diritti_inline_abstract):
	model = Atto_GebevRipartizione
	#raw_id_fields = ("diritto", )

class a_GebevRipartizioneInline(Diritti_inline_abstract):
	model = Autorizzazione_GebevRipartizione
	#raw_id_fields = ("diritto", )

class t_GebevRipartizioneInline(Diritti_inline_abstract):
	model = Template_GebevRipartizione
	#raw_id_fields = ("diritto", )


class WebInline(Diritti_inline_abstract):
	model = Atto_Web
	#raw_id_fields = ("diritto", )

class a_WebInline(Diritti_inline_abstract):
	model = Autorizzazione_Web
	#raw_id_fields = ("diritto", )

class t_WebInline(Diritti_inline_abstract):
	model = Template_Web
	#raw_id_fields = ("diritto", )

class GOffice2Inline(Diritti_inline_abstract):
	model = Atto_GOffice2
	#raw_id_fields = ("diritto", )
	formfield_overrides = {
    	models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

class a_GOffice2Inline(Diritti_inline_abstract):
	model = Autorizzazione_GOffice2
	#raw_id_fields = ("diritto", )
	formfield_overrides = {
    	models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

class t_GOffice2Inline(Diritti_inline_abstract):
	model = Template_GOffice2
	#raw_id_fields = ("diritto", )
	formfield_overrides = {
    	models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


# Modelli Admin

class TestoFissoAdmin(admin_abstract):
	list_display = ('nome', 'tipologia',)
	list_filter = ('tipologia',)
	inlines = [CapoversoInline,]
	save_as = True

class TipoGenericoAdmin(admin_abstract):
	list_display = ('nome', 'nome_de', 'sigla', 'gruppo',)
	search_fields = ['nome', ]

class AttoAdmin(admin_abstract):
	list_display = ['data', 'dipendente', 'url_designazione', 'url_ambito', 'url_password', ]
	search_fields = ['dipendente__cognome', 'dipendente__nome', ]
	list_filter = ['tipo', 'dipendente__ruolo__nome', 'dipendente__servizio__ufficio__nome',]
	ordering = ['-data', ]
	inlines = [
		PasswordInline, 
		DesignazioneInline, 
		GruppoSambaInline, 
		SGVCanaleInline, 
		GOfficeInline, 
		D3GruppoInline, 
		D3DirittoInline, 
		GenericoInline, 
		DirittoReteInline, 
		O365GruppoInline, 
		NextCloudInline, 
		# PortaInline, 
		# WebAppInline, 
		GebevDirittoInline, 
		GebevRipartizioneInline, 
		WebInline,
		GOffice2Inline,
		]
	save_as = True
	radio_fields = {'tipo': admin.VERTICAL, 'amministratore': admin.VERTICAL}
	autocomplete_fields = ['dipendente', ]
	
	def save_formset(self, request, form, formset, change):
		instances = formset.save(commit=False)
		for obj in formset.deleted_objects:
			obj.delete()

		for instance in instances:
			if not instance.id:
				instance.utente_inserimento = request.user
			if request.user.is_superuser:
				instance.utente_admin = request.user
			instance.utente_modifica = request.user
			instance.save()
		formset.save_m2m()
	
	def url_ambito(self, obj):
		txt = u"<a href={}/stampaambito/{}/>AMB</a>"
		return format_html(txt, BASE_URL, obj.id)
	url_ambito.shortdescription = "Ambito"

	def url_password(self, obj):
		txt = u"<a href={}/stampapassword/{}/>PWD</a>"
		return format_html(txt, BASE_URL, obj.id)
	url_password.shortdescription = "Password"
	
	def url_designazione(self, obj):
		txt = u"<a href={}/stampadesignazione/{}/>DES</a>"
		return format_html(txt, BASE_URL, obj.id)
	url_designazione.shortdescription = "Designazione"

class AutorizzazioneAdmin(admin_abstract):
	list_display = ['data', 'ufficio', 'url_autorizzazione', ] 
	search_fields = ['ufficio__nome', ]
	list_filter = ['ufficio', ]
	ordering = ['-data', ]
	inlines = [
		a_GruppoSambaInline, 
		a_SGVCanaleInline, 
		a_GOfficeInline, 
		a_D3GruppoInline, 
		a_D3DirittoInline, 
		a_GenericoInline, 
		a_DirittoReteInline, 
		a_O365GruppoInline, 
		a_NextCloudInline, 
		# a_PortaInline, 
		# a_WebAppInline, 
		a_GebevDirittoInline, 
		a_GebevRipartizioneInline, 
		a_WebInline,
		a_GOffice2Inline,
		]
	save_as = True
	radio_fields = {'amministratore': admin.VERTICAL, }
	autocomplete_fields = ['ufficio', ]
	
	def save_formset(self, request, form, formset, change):
		instances = formset.save(commit=False)
		for obj in formset.deleted_objects:
			obj.delete()

		for instance in instances:
			if not instance.id:
				instance.utente_inserimento = request.user
			if request.user.is_superuser:
				instance.utente_admin = request.user
			instance.utente_modifica = request.user
			instance.save()
		formset.save_m2m()
	
	def url_autorizzazione(self, obj):
		txt = u"<a href={}/stampaautorizzazione/{}/>AUT</a>"
		return format_html(txt, BASE_URL, obj.id)
	url_autorizzazione.shortdescription = "Autorizzazione"
"""
	def url_password(self, obj):
		txt = u"<a href={}/stampapassword/{}/>PWD</a>"
		return format_html(txt, BASE_URL, obj.id)
	url_password.shortdescription = "Password"
	
	def url_designazione(self, obj):
		txt = u"<a href={}/stampadesignazione/{}/>DES</a>"
		return format_html(txt, BASE_URL, obj.id)
	url_designazione.shortdescription = "Designazione"
"""

class TemplateAdmin(admin_abstract):
	list_display = ['data', 'nome', 'autorizzazione', ] 
	search_fields = ['nome', 'autorizzazione_nome', ]
	list_filter = ['autorizzazione', ]
	ordering = ['-data', ]
	inlines = [
		t_GruppoSambaInline, 
		t_SGVCanaleInline, 
		t_GOfficeInline, 
		t_D3GruppoInline, 
		t_D3DirittoInline, 
		t_GenericoInline, 
		t_DirittoReteInline, 
		t_O365GruppoInline, 
		t_NextCloudInline, 
		# t_PortaInline, 
		# t_WebAppInline, 
		t_GebevDirittoInline, 
		t_GebevRipartizioneInline, 
		t_WebInline, 
		t_GOffice2Inline,
		]
	save_as = True
	radio_fields = {'amministratore': admin.VERTICAL, }
	autocomplete_fields = ['autorizzazione', ]
	
	def save_formset(self, request, form, formset, change):
		instances = formset.save(commit=False)
		for obj in formset.deleted_objects:
			obj.delete()

		for instance in instances:
			if not instance.id:
				instance.utente_inserimento = request.user
			if request.user.is_superuser:
				instance.utente_admin = request.user
			instance.utente_modifica = request.user
			instance.save()
		formset.save_m2m()


@admin.register(GruppoSamba)
class GruppoSambaAdmin(DirittoAdmin):
	inlines = [GruppoSamba_ShareInline, ]

 

@admin.register(Porta)	
class PortaAdmin(admin_abstract):
	list_display = ['__str__', 'num_stanza', 'transponder', 'attivo',  ]
	ordering = ['transponder', ]
	list_editable = ['attivo', ]
	#list_editable = ['transponder', ]
#Registrazioni

#admin.site.register(, Admin)
#admin.site.register()

@admin.register(GOffice2)
class GOffice2Admin(DirittoAdmin):
	pass
    

admin.site.register(TipoGenerico, TipoGenericoAdmin)
admin.site.register(Atto, AttoAdmin)
admin.site.register(Autorizzazione, AutorizzazioneAdmin)
# admin.site.register(GruppoSamba, GruppoSambaAdmin)
admin.site.register(Template, TemplateAdmin)
# admin.site.register(Porta, PortaAdmin)
admin.site.register(TestoFisso, TestoFissoAdmin)

admin.site.register(AmbitiPassword)
#admin.site.register(TestoFisso)
admin.site.register(Share)
admin.site.register(Capoverso)


#admin.site.register(Password)

admin.site.register(SGVCanale, DirittoAdmin)
admin.site.register(GOffice, DirittoAdmin)
admin.site.register(D3Gruppo, DirittoAdmin)
admin.site.register(D3Diritto, DirittoAdmin)
admin.site.register(Generico, DirittoAdmin)
admin.site.register(DirittoRete, DirittoAdmin)
admin.site.register(O365Gruppo, DirittoAdmin)
admin.site.register(NextCloud, DirittoAdmin)
#admin.site.register(WebApp)
admin.site.register(GebevDiritto, DirittoAdmin)
admin.site.register(GebevRipartizione, DirittoAdmin)
admin.site.register(Web, DirittoAdmin)

# admin.site.register(Atto_GruppoSamba)
# admin.site.register(Atto_GOffice)
# admin.site.register(Atto_D3Gruppo)
# admin.site.register(Atto_D3Diritto)
# admin.site.register(Atto_Generico)
# admin.site.register(Atto_DirittoRete)
# admin.site.register(Atto_O365Gruppo)
# admin.site.register(Atto_NextCloud)
# admin.site.register(Atto_Porta)
# admin.site.register(Atto_WebApp)
# admin.site.register(Atto_GebevDiritto)
# admin.site.register(Atto_GebevRipartizione)


