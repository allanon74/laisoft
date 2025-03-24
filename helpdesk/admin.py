from django.contrib import admin
from django.db.models.functions import ExtractYear

from django.utils.translation import gettext_lazy as _

from .models import *
# from dipendenti.admin import SearchByYear

# Classi astratte

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

# Filtro

class SearchByYear(admin.SimpleListFilter):
    title = _('anno di apertura ticket')
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        year_list = Ticket.objects.annotate(
            y=ExtractYear('data_apertura')
        ).order_by('y').values_list('y', flat=True).distinct()
        return [
            (str(y), _(str(y))) for y in year_list
        ]

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(data_apertura__year=self.value())
        return queryset

# Inlines

class GruppoSupportoMembriInline(Multi_Inline_abstract):
	model= GruppoSupporto.membri.through
	
class AzioniTicketInline(Multi_Inline_abstract):
	model = Azione
	autocomplete_fields = ('utente',)
	
#	fields = ['utente', 'data_azione', 'note',]

#	read_only = ['data_azione',]
	def get_readonly_fields(self, request, obj):
# 		risp = "[]"
# 		if not obj.id:
# 			risp = ['utente', 'data_azione',]
# 		else:
# 			risp = ['utente', 'data_azione',]
		risp = ['data_azione', ]
		return risp
	
#	def save_model (self, request, obj, form, change):
		
#		obj.utente = request.user
#		super().save_model(request, obj, form, change)
	

class AllegatiTicketInline(Multi_Inline_abstract):
	model = Allegato

# Models

class counterAdmin(admin_abstract):
	list_display = ("id", 'valore', )
	search_field = ("id", "valore",)

class GruppoSupportoAdmin(admin.ModelAdmin):
	list_display = ("nome", )
	#inlines = (GruppoSupportoMembriInline, )
	filter_horizontal = ("membri",)
	
class TipologiaAdmin(admin_abstract):
	list_display = ('sigla', 'nome', )
	search_fields = ('sigla', 'nome',)

class TicketAdmin(admin_abstract):
	list_display = ('nome', 'tipologia', 'persona', 'data_apertura', )
	exclude = ('nome',)
	search_fields = ('nome', 'persona__lastname', )
	autocomplete_fields = ('persona', 'tipologia',)
	list_filter = [SearchByYear, 'tipologia', ]
	
	inlines =(AzioniTicketInline, AllegatiTicketInline,)
	
	def save_model (self, request, obj, form, change):
		if not obj.id:
			obj.utente_apertura = request.user
		obj.utente_modifica = request.user
		
# 		for act in obj.azioni_rel.all():
# 			if not act.utente:
# 				act.utente = request.user
		super().save_model(request, obj, form, change)
	
	
	def get_readonly_fields(self, request, obj=None):
		if request.user.is_staff:
			if request.user.is_superuser:
				return ['nome', 'data_apertura', 'data_modifica', 'data_chiusura', 'utente_apertura', 'utente_modifica', 'utente_chiusura',]
			else:
				return ['nome', 'data_apertura', 'data_modifica', 'data_chiusura', 'utente_apertura', 'utente_modifica', 'utente_chiusura',]

class AzioneAdmin(admin_abstract):
	list_display = ('id', 'ticket', 'data_azione', 'utente', )
	readonly_fields = ('data_azione',)
# registers
#admin.site.register(, Admin)

admin.site.register(counter, counterAdmin)
admin.site.register(GruppoSupporto, GruppoSupportoAdmin)
admin.site.register(Tipologia, TipologiaAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Azione, AzioneAdmin)