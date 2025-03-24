from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin as SModelAdmin
from django_summernote.admin import SummernoteInlineModelAdmin as SInlineModelAdmin

from .models import *

from django.utils.translation import gettext_lazy as _

# Admin DIPENDENTI

# admin actions

@admin.action(description=_("NUOVO DIPENDENTE: Invia e-mail al consorzio (richiesta nuova matricola)."))
def email_sgv(modeladmin, request, queryset):
	ml = Mail.objects.get(nome="sgv")
	for obj in queryset:
		obj.mail(ml)

@admin.action(description=_("NUOVO DIPENDENTE: Invia e-mail agli uffici comunali (dopo aver inserito la matricola)."))
def email_com(modeladmin, request, queryset):
	ml = Mail.objects.get(nome="com")
	for obj in queryset:
		obj.mail(ml)

@admin.action(description=_("NUOVO DIPENDENTE: Invia e-mail a Presenze (dopo aver inserito userid)."))
def email_pre(modeladmin, request, queryset):
	ml = Mail.objects.get(nome="pre")
	for obj in queryset:
		obj.mail(ml)


@admin.action(description=_("CESSAZIONE DIPENDENTE: Invia e-mail."))
def email_ces(modeladmin, request, queryset):
	ml = Mail.objects.get(nome="ces")
	for obj in queryset:
		obj.mail(ml)

@admin.action(description=_("MODIFICA DIPENDENTE: Invia e-mail."))
def email_mod(modeladmin, request, queryset):
	ml = Mail.objects.get(nome="mod")
	for obj in queryset:
		obj.mail(ml)

# Filter model



    
# Register your models here.

class Multi_abstract(admin.ModelAdmin):
	list_display = ('nome', 'nome_it_m', )
	search_fields = ['nome', 'nome_it_m', 'nome_it_f', 'nome_dt_m', 'nome_dt_f', ]
	save_on_top = True 
	
	class Meta:
		abstract = True

class Multi_Inline_abstract(admin.TabularInline):
	#ordering = ('nome',)
	extra = 0
	#min_num = 1
	
	class Meta:
		abstract = True




class DipendenteRuoloInline(Multi_Inline_abstract):
	model = Dipendente_Ruolo

class DipendenteServizioInline(Multi_Inline_abstract):
	model = Dipendente_Servizio

class ServizioResponsabileInline(Multi_Inline_abstract):
	model = Servizio_Responsabile

class UfficioDirigenteInline(Multi_Inline_abstract):
	model = Ufficio_Dirigente

class DipendenteQualificaInline(Multi_Inline_abstract):
	model = Dipendente_Qualifica

class VoceCapoversoInline(SInlineModelAdmin):#
	model = Capoverso
	template = "admin/edit_inline/tabular.html"
	summernote_fields = ['testo', ]
	extra = 1

class SezioneVoceInline(SInlineModelAdmin):#
	model = Voce
	template = "admin/edit_inline/tabular.html"
	summernote_fields = ['testo', ]
	extra = 1

class PaginaSezioneInline(SInlineModelAdmin):#
	model = Sezione
	template = "admin/edit_inline/tabular.html"
	summernote_fields = ['testo', ]
	extra = 1

class VoceAllegatoInline(SInlineModelAdmin):
	model=Allegato
	template = "admin/edit_inline/tabular.html"
	extra=1

# 	fieldsets = (
# 		(None, {
# 			'fields': ('dipendente', 'rapportolavoro', 'determinato', 'qualifica','data_da', 'data_a', )	
# 		}),
# 	)

class ServizioUfficioInline(Multi_Inline_abstract):
	model = Servizio_Ufficio
	
class LivelloQualificaInline (Multi_Inline_abstract):
	model = Qualifica

class RapportoLavoroAdmin(admin.ModelAdmin):
	list_display = ('descrizione', 'n_minuti', 'coefficiente', )
	search_fields = ['descrizione',]
	save_on_top = True

class DipendenteAdmin(admin.ModelAdmin):
	list_display = ('cognome', 'nome', 'matricola', 'userid', 'email', 'telefono', 'num_servizi', )
	list_editable = ('telefono', )
	search_fields = ['cognome', 'nome', 'userid',  ]
	list_filter = ('sesso', 'ruolo__nome', 'qualifica__livello__livello', 'attivo', 'catprotetta', 'servizio__nome', 'servizio__ufficio__nome',)
	ordering =('cognome', 'nome', )
	save_on_top = True 
	inlines = (DipendenteRuoloInline, DipendenteQualificaInline, DipendenteServizioInline, )
	radio_fields = {"sesso": admin.HORIZONTAL, "patentino": admin.HORIZONTAL, }
	actions = [email_sgv, email_com, email_pre, email_ces, email_mod, ]
	
class DirigenteAdmin(admin.ModelAdmin):
	list_display = ('matricola', 'nome', 'cognome', 'userid', 'email', 'telefono', 'cellulare', )
	search_fields = ['cognome', 'nome', 'userid',  ]
	list_filter = ('ruolo__nome', 'servizio__nome', 'servizio__ufficio__nome', )
	ordering =('cognome', 'nome', )
	save_on_top = True 
	inlines = (UfficioDirigenteInline, ServizioResponsabileInline, )
	radio_fields = {"sesso": admin.HORIZONTAL}	

class MailAdmin(SModelAdmin):
	list_display = ['nome', 'oggetto', ]
	search_fields = ['nome', 'oggetto', ]
	save_on_top = True
	summernote_fields= ["testo", ]
	save_as = True
	
	def get_readonly_fields(self, request, obj=None):
		if request.user.is_staff:
			if request.user.is_superuser:
				return []
			else:
				return['nome',]

	
class RuoloAdmin(Multi_abstract):
	list_filter = ('dirigente', 'responsabile', 'segretario', 'sindaco', 'ammsistema')
	#inlines =(DipendenteRuoloInline, )
	
class LivelloAdmin(admin.ModelAdmin):
	list_display = ('livello', 'indice', 'coefficiente', )
	search_fields = ['livello', ]
	inlines = (LivelloQualificaInline, )
	
	
class UfficioAdmin(Multi_abstract):
	list_display = ('nome', 'nome_it_m', 'dirigente_al', 'formula_responsabile_it', 'formula_responsabile_dt',)
	inlines = (ServizioUfficioInline, UfficioDirigenteInline, )
	list_editable = ('formula_responsabile_it', 'formula_responsabile_dt', )
	
class ServizioAdmin(Multi_abstract):
	list_display = ('nome', 'nome_it_m', 'ufficio_al', 'responsabile_al', 'cdc', 'telefono', )
	inlines = (ServizioResponsabileInline, ServizioUfficioInline, DipendenteServizioInline, )
	list_editable = ('cdc', )

class QualificaAdmin(Multi_abstract):
	list_display = ('nome', 'nome_it_m', 'livello', )
	inlines = (DipendenteQualificaInline, )
	#pass
	
class LogoAdmin(admin.ModelAdmin):
	list_display = ('descrizione', 'id', )

class VoceAdmin(SModelAdmin):
	list_display = ["nome", "titolo", "pubblicato", ]
	search_fields = ["nome", "titolo", ]
	inlines = (VoceCapoversoInline,  )
	list_editable = ["pubblicato", ]
	summernote_fields= ["testo", ]
	list_filter = ['sezione', 'sezione__pagina', ]

class SezioneAdmin(VoceAdmin):
	inlines = [SezioneVoceInline, ]
	list_filter = ['pagina', ]

class PaginaAdmin(VoceAdmin):
	inlines = [PaginaSezioneInline, ]

class ImmagineAdmin (admin.ModelAdmin):
	list_display = ['nome', 'descrizione', ]
	search_fields = ['nome', 'descrizione', ]
	save_on_top = True

class AllegatoAdmin (admin.ModelAdmin):
	list_display = ['nome', 'descrizione', ]
	search_fields = ['nome', 'descrizione', ]
	save_on_top = True

admin.site.register(Dipendente, DipendenteAdmin)
admin.site.register(Dirigente, DirigenteAdmin)
admin.site.register(Ruolo, RuoloAdmin)
admin.site.register(Livello, LivelloAdmin)
admin.site.register(Ufficio, UfficioAdmin)
admin.site.register(Servizio, ServizioAdmin)
admin.site.register(Qualifica, QualificaAdmin)
admin.site.register(RapportoLavoro, RapportoLavoroAdmin)
admin.site.register(Logo, LogoAdmin)
admin.site.register(Mail, MailAdmin)
admin.site.register(Voce, VoceAdmin)
admin.site.register(Sezione, SezioneAdmin)
admin.site.register(Pagina, PaginaAdmin)
admin.site.register(Immagine, ImmagineAdmin)
admin.site.register(Allegato, AllegatoAdmin)


#admin.site.register(, Admin)
