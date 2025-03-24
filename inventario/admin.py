from django.contrib import admin
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from parler.admin import TranslatableAdmin, TranslatableTabularInline

from django.utils.translation import gettext_lazy as _

from .models import Edificio, Stanza, Marca, Tipo, Oggetto, Status, Record, Fornitore

# modelli astratti

class Admin_a(admin.ModelAdmin):
    save_on_top = True
    list_display = ['id',]
    list_filter = []
    search_fields = []
    ordering = ['-data_creazione',]
    readonly_fields = ['id', 'data_creazione', 'data_modifica', 'creato_da', 'modificato_da',]   
    fieldsets = (
        (None, {'fields': ()}),
        (_('Dati Interni'), {'fields' : ('id', 'data_creazione', 'data_modifica','creato_da', 'modificato_da',  )}),
    )

    class Meta:
        abstract = True

class Nome_a(Admin_a):
    list_display = ['nome_breve',  ]
    search_fields = ['nome_breve', 'descrizione', ]
    fieldsets = (
        (None, {'fields': ('nome_breve', 'descrizione')}),
        (_('Dati Interni'), {'fields' : ('id', 'data_creazione', 'data_modifica','creato_da', 'modificato_da',  )}),
    )

class ItDe_a(TranslatableAdmin):
    list_display = ['nome_breve', 'color_square',]
    search_fields= [
        'translations__nome_breve',
        'translations__descrizione',
        ]
    list_filter = []
    #search_fields = []
    save_on_top = True
    ordering = ['-data_creazione',]
    readonly_fields = ['id', 'data_creazione', 'data_modifica', 'creato_da', 'modificato_da',]
    fieldsets = (
        (None, {'fields': ('nome_breve', 'descrizione', 'colore', 'fa_icon', 'fa_visible')}),
        (_('Dati Interni'), {'fields' : ('id', 'data_creazione', 'data_modifica','creato_da', 'modificato_da',  )}),
    )

    def color_square(self, obj):
        #txt = u'<div style="width:12px;heigth:12px;background-color:{};"></div>'
        txt = u'<p style="background-color:{};color:{};text-align:center;">{}</p>'
        return format_html(txt, obj.colore, obj.colore_testo(), obj.colore)
    color_square.short_description = _("Colore")
	
    class Meta:
        abstract = True
  
  
class Inline_a(admin.TabularInline):
    extra = 1
    min_num = 0
    readonly_fields = ['id', 'data_creazione', 'data_modifica', 'creato_da', 'modificato_da',]

    class Meta:
        abstract = True
  
  
# classi Inline

class RecordInline(Inline_a):
    model = Record


class OggettoInline(Inline_a):
    model = Oggetto
      

class StanzaInline(Inline_a, TranslatableTabularInline):
    model = Stanza

  
# Register your models here.

@admin.register(Fornitore)
class FornitoreAdmin(Nome_a):
    list_display = ['nome_breve','telefono', 'cel', 'contatto']
    inlines = [RecordInline, ]
    
    fieldsets = (
        (None, {'fields': ('nome_breve', 'descrizione', 'telefono', 'cel', 'contatto', )}),
        (_('Dati Interni'), {'fields' : ('id', 'data_creazione', 'data_modifica','creato_da', 'modificato_da',  )}),
    )


@admin.register(Edificio)
class EdificioAdmin(ItDe_a):
    inlines = [StanzaInline, ]


@admin.register(Stanza)
class StanzaAdmin(ItDe_a):
    list_display = ('nome_breve', 'edificio', 'color_square', )
    # autocomplete_fields = ['edificio',]
    radio_fields = {'edificio': admin.VERTICAL, }
    inlines = [RecordInline, ]
    

    
    fieldsets = (
         (None, 
            {'fields': ('nome_breve', 'edificio', 'descrizione', )}
        ),
         (_('Dati Interni'), 
          {'fields' : ('id', 'data_creazione', 'data_modifica', 'modificato_da',  )}
        ),
    )

@admin.register(Marca)
class MarcaAdmin(Nome_a):
    inlines = [OggettoInline, ]


@admin.register(Tipo)
class TipoAdmin(ItDe_a):
    
   inlines = [OggettoInline, ]


@admin.register(Oggetto)
class OggettoAdmin(Nome_a):
    list_display = ['nome_breve', 'marca', 'tipo', ]
    autocomplete_fields = ['tipo', 'marca', ]
    inlines = [RecordInline, ]   
    
    fieldsets = (
         (None, 
            {'fields': ('nome_breve', 'marca', 'tipo', 'descrizione', )}
        ),
         (_('Dati Interni'), 
          {'fields' : ('id', 'data_creazione', 'data_modifica', 'modificato_da',  )}
        ),
    )

@admin.register(Status)
class StatusAdmin(ItDe_a):
    inlines = [RecordInline, ]
    pass
    
@admin.register(Record)
class RecordAdmin(Admin_a, SimpleHistoryAdmin):
    list_display = ["asset", "oggetto", "data_acquisto", "stanza", "dipendente", "status"]
    list_filter = ["oggetto", "stanza", "status",]
    autocomplete_fields = ['oggetto', 'stanza', 'dipendente', 'fornitore']
    search_fields = Admin_a.search_fields + ['oggetto__nome_breve', 'stanza__translations__nome_breve', 'stanza__edificio__translations__nome_breve', 'dipendente__cognome', 'dipendente__nome', 'fornitore__nome_breve']

    radio_fields = {'status': admin.VERTICAL, }
    
    fieldsets = (
         (None, 
            {'fields': ('oggetto', 'fornitore', 'data_acquisto', 'data_fine_garanzia', 'stanza', 'status', 'dipendente', 'seriale', 'remark1', 'remark2', 'remark3', 'note')}
        ),
         (_('Dati Interni'), 
          {'fields' : ('id', 'data_creazione', 'data_modifica', 'modificato_da',  )}
        ),
     )