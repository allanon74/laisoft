from django.contrib import admin
from .models import *
"""
# Admin PERSONALE
# Register your models here.

class Multi_abstract(admin.ModelAdmin):
	list_display = ('id', 'nome', )
	search_fields = ['nome', 'nome_it_m', 'nome_it_f', 'nome_dt_m', 'nome_dt_f', ]
	save_on_top = True 
	
	class Meta:
		abstract = True

class Multi_Inline_abstract(admin.TabularInline):
	#ordering = ('nome',)
	extra = 1
	
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

class ServizioUfficioInline(Multi_Inline_abstract):
	model = Servizio_Ufficio
	
class LivelloQualificaInline (Multi_Inline_abstract):
	model = Qualifica


class DipendenteAdmin(admin.ModelAdmin):
	list_display = ('id', 'nome', 'cognome', 'userid', 'email', 'telefono', 'cellulare', 'catprotetta',)
	search_fields = ['cognome', 'nome', 'userid',  ]
	list_filter = ('ruolo__nome', 'qualifica__livello__livello', 'catprotetta', 'servizio__nome', 'servizio__ufficio__nome', )
	ordering =('cognome', 'nome', )
	save_on_top = True 
	inlines = (DipendenteRuoloInline, DipendenteQualificaInline, DipendenteServizioInline, )
	
class RuoloAdmin(Multi_abstract):
	list_filter = ('dirigente', 'coordinatore', 'responsabile', 'segretario', 'sindaco', 'ammsistema')
	inlines =(DipendenteRuoloInline, )
	
class LivelloAdmin(admin.ModelAdmin):
	list_display = ('livello', 'indice', 'coefficiente', )
	search_fields = ['livello', ]
	inlines = (LivelloQualificaInline, )
	
	
class UfficioAdmin(Multi_abstract):
	inlines = (ServizioUfficioInline, )
	#pass
	
class ServizioAdmin(Multi_abstract):
	inlines = (ServizioResponsabileInline, ServizioUfficioInline, )
	#pass

class QualificaAdmin(Multi_abstract):
	inlines = (DipendenteQualificaInline, )
	#pass

admin.site.register(Dipendente, DipendenteAdmin)
admin.site.register(Ruolo, RuoloAdmin)
admin.site.register(Livello, LivelloAdmin)
admin.site.register(Ufficio, UfficioAdmin)
admin.site.register(Servizio, ServizioAdmin)
admin.site.register(Qualifica, QualificaAdmin)


#admin.site.register(, Admin)
"""