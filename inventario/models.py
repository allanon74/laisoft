from django.db import models
from django.utils import timezone
from colorfield.fields import ColorField

from parler.models import TranslatableModel, TranslatedFields, TranslatedFieldsModel, TranslatedField
from django.utils.translation import gettext_lazy as _


from dipendenti.models import Dipendente

from django_currentuser.middleware import ( get_current_user, get_current_authenticated_user)
from django_currentuser.db.models import CurrentUserField

from simple_history.models import HistoricalRecords
from simple_history import register

from gic.models import ComplementaryColor, luminance, hex_to_rgb, rgb_to_hex 


DEFAULT="DEF"

class Default():
    @classmethod
    def stanza(self):
        return Stanza.default()
    
    @classmethod
    def edificio(self):
        return Edificio.default()
    
    @classmethod
    def status(self):
        return Status.default()
        
    


# Create your models here.

register(Dipendente)

# classi astratte 


class Base_a(models.Model):

    """
    Classe astratta di base a tutti gli oggetti del progetto\n
    id: autofield di ID dell'oggetto\n
    data_creazione: data automatica di creazione\n
    data_modifica = data automatica di ultima modifica\n
    """

    id = models.AutoField(_("Codice Identificativo"), primary_key=True, ) 
    data_creazione = models.DateTimeField(
        _("Data di creazione"),
        auto_now_add = True,
        )
    data_modifica = models.DateTimeField(
        _("Data di ultima modifica"),
        auto_now = True,
        )
    creato_da = CurrentUserField(related_name = "+")
    modificato_da = CurrentUserField(on_update=True)
    
    class Meta:
        abstract = True



class Nome_a(models.Model):
    nome_breve = models.CharField(_("Nome Breve"), max_length = 30,)
    descrizione = models.TextField(_("Descrizione"), null=True, blank=True,)   

    def __str__(self):
        text = "{nome}"
        return text.format(nome = self.nome_breve)
    
    class Meta:
        abstract = True
   


class ItDe_a(TranslatableModel):

    """
    Classe con i campi di default per descrizione in italiano e tedesco:\n
    nome_breve: nome per le referenze interne e l'admin site\n
    nome_it e *_de = nomi brevi nelle due lingue per l'interfaccia web\n
    descrizione_it e *_de: descrizioni dettagliate nelle due lingue\n
    colore: esadecimale del colore associato per associazioni cromatiche\n
    """
    nome_breve = TranslatedField()
    descrizione = TranslatedField()

    colore = ColorField(verbose_name=_("Colore"))
    fa_icon = models.CharField(
        _("Classe icona FontAwesome"),
        max_length=60,
        default="fa-solid fa-circle"
        )
    fa_visible = models.BooleanField(
        _("Icona Visibile"),
        default = True,
        )

    def colore_testo(self):
        testo ="#ffffff"
        lum = luminance(hex_to_rgb(self.colore))
        if lum <140 and lum >55:
            testo = "#ffffff"
        elif lum >139 and lum <201:
            testo = "#000000"
        else: testo = ComplementaryColor(self.colore)
        return testo
	
    def __str__(self):
        text = "{nome}"
        return text.format(nome = self.nome_breve)
    
    class Meta:
        abstract = True
        
  
class ItDe_aTranslation(TranslatedFieldsModel):
    # master = models.ForeignKey(ItDe_a, related_name='translations', null=True, on_delete= models.PROTECT)
    nome_breve = models.CharField(
        _("Nome Breve"),
        max_length = 30,
    )
    descrizione = models.TextField(
        _("Descrizione"),
        null=True, blank=True,
     )
    class Meta:
        abstract = True


  
# modelli

class Fornitore(Base_a, Nome_a):
    telefono = models.CharField(_("Numero di telefono"), max_length=15, null=True, blank=True)
    cel = models.CharField(_("Numero di cellulare"), max_length=15, null=True, blank=True)
    contatto = models.CharField(_("Persona di contatto"), max_length=120, null=True, blank=True)
    
    class Meta:
        verbose_name = "Fornitore"
        verbose_name_plural = "Fornitori"




class Edificio(Base_a, ItDe_a):
    sigla = models.CharField(_("Sigla"), max_length=3, null=True, blank=True)
        
    class Meta:
        verbose_name = _("Edificio")
        verbose_name_plural = _("Edifici")
        
    @classmethod
    def default(self):
        a = self.objects.filter(sigla=DEFAULT).order_by("-data_creazione")
        res = None
        if a.count() == 0:
            res = self(
                sigla=DEFAULT,
                nome_breve="Municipio", 
            )
            res.save()
        else:
            res = a[0]
        return res

class EdificioTanslation(ItDe_aTranslation):
    master = models.ForeignKey(Edificio, related_name='translations', null=True, on_delete= models.CASCADE)


class Stanza(Base_a, ItDe_a):
    edificio = models.ForeignKey(Edificio, verbose_name = _("Edificio"), on_delete=models.PROTECT,
                                  default=Default.edificio, 
                                 )
    sigla = models.CharField(_("Sigla"), max_length=3, null=True, blank=True)

    def __str__(self):
        text = "{edif} -> {stan}"
        return text.format(edif=self.edificio.nome_breve, stan = self.nome_breve)
    
    class Meta:
        verbose_name = _("Stanza")
        verbose_name_plural = _("Stanze")
        
    @classmethod
    def default(self):
        a = self.objects.filter(sigla=DEFAULT).order_by("-data_creazione")
        res = None
        if a.count() == 0:
            res = self(
                sigla=DEFAULT,
                edificio=Edificio.default(),
                nome_breve="Magazzino EDP", 
            )
            res.save()
        else:
            res = a[0]
        return res

class StanzaTanslation(ItDe_aTranslation):
    master = models.ForeignKey(Stanza, related_name='translations', null=True, on_delete= models.CASCADE)
    
    
class Marca(Base_a, Nome_a):
    
    class Meta:
        verbose_name = _("Marca")
        verbose_name_plural = _("Marche")



# class Tipologia(Base_a, ItDe_a):
#     sigla = models.CharField(_("Sigla"), max_length=3, null=True, blank=True)
        
#     class Meta:
#         verbose_name = _("Tipo di oggetto")
#         verbose_name_plural = _("Tipi di oggetto")
        
# class TipologiaTranslation(ItDe_aTranslation):
#     master = models.ForeignKey(Tipologia, related_name="translations", null=True, on_delete= models.CASCADE)

class Tipo(Base_a, ItDe_a):
    sigla = models.CharField(_("Sigla"), max_length=3, null=True, blank=True)
        
    class Meta:
        verbose_name = _("Tipo di oggetto")
        verbose_name_plural = _("Tipi di oggetto")
        
class TipoTranslation(ItDe_aTranslation):
    master = models.ForeignKey(Tipo, related_name="translations", null=True, on_delete= models.CASCADE)



class Oggetto(Base_a, Nome_a):
    marca = models.ForeignKey(Marca, verbose_name=_("Marca"), null=True, on_delete=models.PROTECT)
    tipo = models.ForeignKey(Tipo, verbose_name=_("Tipo di oggetto"), null=True, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = _("Oggetto")
        verbose_name_plural = _("Oggetti")
        
    def __str__(self):
        text = "{tipo} - {mrc} {mdl}"
        return text.format(tipo=self.tipo.nome_breve, mrc=self.marca.nome_breve, mdl=self.nome_breve)

class Status(Base_a, ItDe_a):
    sigla = models.CharField(_("Sigla"), max_length=3, null=True, blank=True)
    
    class Meta:
        verbose_name = _("Status")
        verbose_name_plural = _("Status")        

    @classmethod
    def default(self):
        a = self.objects.filter(sigla=DEFAULT).order_by("-data_creazione")
        res = None
        if a.count() == 0:
            res = self(
                sigla=DEFAULT,
                nome_breve="Disponibile", 
            )
            res.save()
        else:
            res = a[0]
        return res

class StatusTanslation(ItDe_aTranslation):
    master = models.ForeignKey(Status, related_name='translations', null=True, on_delete= models.CASCADE)
 
class Record(Base_a):
    seriale = models.CharField(_("Numero Seriale"), max_length=30, )
    oggetto = models.ForeignKey(Oggetto, verbose_name=_("Oggetto"), on_delete=models.PROTECT)
    fornitore = models.ForeignKey(Fornitore, verbose_name=_("Fornitore"), on_delete=models.PROTECT)
    stanza = models.ForeignKey(Stanza, verbose_name=_("Stanza"), on_delete=models.PROTECT,
                                default=Default.stanza,
                               )
    status = models.ForeignKey(Status, verbose_name=_("Status"), on_delete=models.PROTECT,
                                default=Default.status,
                               )
    dipendente = models.ForeignKey(Dipendente, verbose_name=_("Dipendente consegnatario"), null=True, blank=True, on_delete=models.PROTECT)
    data_acquisto = models.DateField(_("Data di Acquisto"), null=True, blank=True)
    data_fine_garanzia = models.DateField(_("Data di Fine Garanzia"), null=True, blank=True)
    remark1 = models.CharField(_("Remark 1 (MAC Address)"), max_length=30, null=True, blank=True)
    remark2 = models.CharField(_("Remark 2"), max_length=30, null=True, blank=True)
    remark3 = models.CharField(_("Remark 3"), max_length=30, null=True, blank=True)
    note = models.TextField(_("Note"), null=True, blank=True)
    
    history = HistoricalRecords()
    

    
    @property
    def asset(self):
        return "A{ast}".format(ast=str(self.id).zfill(8))
    
    
    def __str__(self):
        
        text = "{num} - {ogg} -> {place}".format(num=self.asset, ogg=self.oggetto, place = self.stanza)
        return text
    
    class Meta:
        verbose_name = _("Record")
        verbose_name_plural = _("Records")