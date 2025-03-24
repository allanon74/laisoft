from django.contrib import admin
from .models import Tipo, VoceTitolario, Gruppo

class TipoAdmin(admin.ModelAdmin):
	list_display = ('nome', 'classifica', 'titolari', )
	search_fields = ['nome', ]
	list_filter = ('temporaneo', )
	ordering = ('nome', )
	save_on_top = True
	filter_horizontal = ('visibilita', )

class VoceTitolarioAdmin(admin.ModelAdmin):
	list_display = ('id', 'descrizione', 'order', )
	ordering = ('order', )
	# list_editable = ('order', )
	list_per_page = 150

class GruppoAdmin(admin.ModelAdmin):
	list_display = ('id', 'descrizione')
	ordering = ('id', )
	
admin.site.register(Tipo, TipoAdmin)
admin.site.register(VoceTitolario, VoceTitolarioAdmin)
admin.site.register(Gruppo, GruppoAdmin)



# Register your models here.
