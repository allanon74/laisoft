from django.contrib import admin
from .models import *
from django import forms




def mail_giorno(modeladmin, request, queryset):
	for gi in queryset:
		tur = Turno.objects.all().filter(giorno = gi)
		for tu in tur:
			if tu.persona.email != "" and tu.avvisato == False:
				tu.avvisa()
				#queryset.filter(turno__id=tu.id).update(turno.avvisato=True)
				tu.avvisato = True
				tu.save()
		
mail_giorno.short_description = "Avvisa le persone non avvisate di questo/i giorno/i"


def mail_turno(modeladmin, request, queryset):
	for tu in queryset:
		if tu.persona.email != "" and tu.persona.email is not None and tu.avvisato == False:
			tu.avvisa()
			tu.avvisato=True
			tu.save()

mail_turno.short_description = "Avvisa chi non avvisato per questo/i turno/i"
		
		
class TurnoInline(admin.TabularInline):
	model = Turno
	ordering = ('fascia', 'ruolo', 'persona', )
	extra = 1

class PersonaAdmin(admin.ModelAdmin):
	list_display = ('cognome', 'nome', 'telefono', 'email', 'note', )
	search_fields =['nome', 'cognome', 'note', 'telefono', 'email', ]
	list_filter = ('disponibilita', 'capacita', )
	ordering = ('cognome', 'nome', )
	save_on_top = True
	inlines = (TurnoInline, )
#	filter_horizontal = ('disponibilita', )
	formfield_overrides = {
		models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
	}
	
	
class RuoloAdmin(admin.ModelAdmin):
	list_display = ('nome', 'richiesti', 'descrizione', )
	search_fields = ['nome', 'descrizione', ]
	ordering = ('ordine', 'nome', )
	list_editable = ['richiesti',  ]
	save_on_top = True
	inlines = [TurnoInline, ]
	
class FasciaAdmin(admin.ModelAdmin):
	list_display = ('nome', 'descrizione', 'ordine', 'desc_breve', )
	search_fields = ['nome', 'descrizione', ]
	ordering = ('ordine', 'nome', )
	list_editable = ['desc_breve', 'ordine', ]
	save_on_top = True
	inlines = [TurnoInline, ]	

class GiornoAdmin(admin.ModelAdmin):
	list_display = ('data', 'note', )
	search_fields = ['data', 'note' ]
	ordering = ('data', )
	save_on_top = True
	inlines = [TurnoInline, ]
	actions = [mail_giorno]
	
class TurnoAdmin(admin.ModelAdmin):
	list_display = ('giorno', 'fascia', 'ruolo', 'persona', 'avvisato', 'confermato')
	search_fields = ['persona__cognome', 'persona__nome', ]
	list_filter = ('avvisato', 'confermato', 'giorno', 'ruolo', )
	list_editable = ['avvisato', 'confermato', ]
	ordering = ('giorno', 'fascia', )
	save_on_top = True
	actions = [mail_turno]
	

	


	
admin.site.register(Persona, PersonaAdmin)
admin.site.register(Ruolo, RuoloAdmin)
admin.site.register(Fascia, FasciaAdmin)
admin.site.register(Turno, TurnoAdmin)
admin.site.register(Giorno, GiornoAdmin)


# admin.site.register(, Admin)



# Register your models here.
