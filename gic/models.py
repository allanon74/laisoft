from django.contrib.gis.db import models
from parler.models import TranslatableModel, TranslatedFields, TranslatedFieldsModel, TranslatedField
from colorfield.fields import ColorField
from django.utils import timezone
import datetime
import copy
from django.db.models import Count, F, When, Case, Value, ExpressionWrapper as EW, Min, Max

import humanize

from dipendenti.models import Servizio



#from .fotoform import FotoForm  


from django.contrib import admin

#from .views import VistaMain, VistaOperai, VistaCollaboratori, VistaIntervento, VistaInterventi, VistaSegnalazione, VistaSegnalazioni

# import gic.views

import gic

# from thumbnails.fields import ImageField

from django.utils.translation import gettext_lazy as _

from dipendenti.models import Dipendente




# funzioni generali 

def call(date):
	if callable(date):
		return date()
	else:
		return date

def ComplementaryColor(my_hex):
	"""Returns complementary RGB color

	Example:
			>>>>complementaryColor('FFFFFF')
			'000000'
			"""
	init_char = ""
	if my_hex[0] == '#':
		my_hex = my_hex[1:]
		init_char = "#"
	rgb = (my_hex[0:2], my_hex[2:4], my_hex[4:6])
	comp = ['%02X' % (255 - int(a, 16)) for a in rgb]
	result =  ''.join(comp)
	return init_char + result

def hex_to_rgb(value):
	"""Return (red, green, blue) for the color given as #rrggbb."""
	value = value.lstrip('#')
	lv = len(value)
	return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rgb_to_hex(red, green, blue):
	"""Return color as #rrggbb for the given color values."""
	return '#%02x%02x%02x' % (red, green, blue)

def luminance (rgb = {}):
	l = 0.216 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
	return l


# Costanti ed enumerazioni

INT_PRIORITA = 20


STATO = "TO"
SEGNORIG = "SO"
SEGNTIPO = "ST"
FOTO = "FO"
ASSENZA = "AS"
REPERIBILITA = "RE"
INTERNO = "IN"



	
"""
enumerazione per differenziare le varie tipologie esistenti \n
STATO: vale per tutti gli oggetti ereditati da Status_a (aperto, chiuso , verificato...)\n
SEGNORIG: tipologie di origine delle segnalazioni\n
SEGNTIPO: tipologia di segnalazioni\n
FOTO: tipologie di foto (inizio, fine, corso di svolgimento)\n
ASSENZA: tipi di assenza(malattia, ferie, corso...)\n
REPERIBILITA: tipi di reperibilità (ordinaria, neve)\n
"""
tipologie = {
	STATO : _("Stato"),
	SEGNORIG : _("Origine Segnalazione"),
	SEGNTIPO : _("Tipologia Segnalazione"),
	FOTO : _("Tipologia di Foto"),
	ASSENZA : _("Tipologia di assenza"),
	REPERIBILITA : _("Tipologia di Reperibilità"),
	INTERNO : _("Interno"),
	}

IT = "it"
DE = "de"
EN = "en"

lingue = [
	(IT, "Italiano"),
	(DE, "Deutsch"),
	(EN, "English"),
	]


si_no = (
		(True, _("Sì")),
		(False, _("No"))
		)


SEGNALAZIONE = "Segnalazione"
INTERVENTO = "Intervento"
TEAM = "Team"
LAVORO = "Lavoro"
SALVA = "Salva"
COLLABORATORE = "Collaboratore"
TEMPI_LAVORO = "Tempilavoro"

modelli = {
	SEGNALAZIONE : _("Segnalazione"),
	INTERVENTO : _("Intervento"),
	TEAM :  _("Team"),
	LAVORO :  _("Lavoro"),
	TEMPI_LAVORO : _("Tempi di Lavoro"),
	COLLABORATORE : _("Collaboratore"),
	SALVA : _('Pulsante "Salva"'),
	FOTO : _('Foto'),

}

temi = [
		('a', _('Tema') + ' a'),
		('b', _('Tema') + ' b'),
		('c', _('Tema') + ' c'),
		('d', _('Tema') + ' d'),
		('e', _('Tema') + ' e'),
		('f', _('Tema') + ' f'),
		('g', _('Tema') + ' g'),
		('h', _('Tema') + ' h'),
		('i', _('Tema') + ' i'),
		('j', _('Tema') + ' j'),
		('k', _('Tema') + ' k'),
		('l', _('Tema') + ' l'),
		('m', _('Tema') + ' m'),
		]

ruoli = {
	"LS_GIC_operaio": "operaio",
	"LS_GIC_capocantiere" : "capocantiere",
	"LS_GIC_caposquadra" :  "caposquadra",
	"LS_GIC_ufficio" :  "ufficio",
	"LS_GIC_struttura" : "struttura",
	"LS_GIC_coordinatore" : "coordinatore",
	}

# modelli astratti

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
	class Meta:
		abstract = True

class Gis_a(models.Model):
	
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
	
	@property	
	def icona(self):
		
		tag = ""
		if self.fa_visible:
			tag = '<i class="{classe} icon_tt" style="color:{colore};float:right;"><span class="icon_text">&nbsp;{tipo}:&nbsp;{nome_breve}&nbsp;</span></i>'.format(classe=self.fa_icon, colore=self.colore, tipo=_("Tag Evento"), nome_breve=self.nome_breve)
			
		return tag
	
	class Meta:
		abstract = True

  
class ItDe_aTranslation(TranslatedFieldsModel):
#	master = models.ForeignKey(ItDe_a, related_name='translations', null=True, on_delete= models.PROTECT)
	nome_breve = models.CharField(
			_("Nome Breve"),
			max_length = 30,
			)
	descrizione = models.TextField(
			_("Descrizione"),
			)
	class Meta:
		abstract = True

		
class Periodic_a(models.Model):
	
	"""
	classe per riportare i campi relativi agli elementi periodici\n
	periodico: boolean per indicare se l'elemento è periodico\n
	periodo: numero di giorni dopo la chiusura in cui l'evento si ripete\n
	cicli: nomero di cicli che si devono ripetere; se vuoto si ripete all'infinito\n
	duplicare: se vero, duplica gli elementi gerarchicamente sottostanti\n
	"""
	
	periodico = models.BooleanField(
		_("Elemento Periodico"),
		default = False,
		)
	periodo = models.IntegerField(
		_("Periodo"),
		help_text = _("Numero di giorni successivi alla chiusura dopo i quali ripetere l'elemento"),
		null = True, blank = True,
		)
	cicli = models.IntegerField(
		_("Cicli"), 
		help_text = _("Numero di volte che si intende ripetere l'elemento. Se non valorizzato, allora si ripete all'infinito."),
		null = True, blank = True,
		)
	duplicare = models.BooleanField(
		_("Duplicare elementi sottostanti"),
		default = False,
		)

	class Meta:
		abstract = True

		
class Description_a(models.Model):
	
	"""
	classe con i campi standard di descrizione degli elementi\n
	oggetto: descrizione sintetica\n
	descrizione: descrizione completa\n
	note: annotazioni aggiuntive\n
	"""
	
	oggetto = models.CharField(
		_("Oggetto"), 
		max_length = 250,
		)
	descrizione = models.TextField(
		_("Descrizione"),
		null = True, blank = True,
		)
	note = models.TextField(
		_("Note"),
		null = True, blank = True,
		)
	
	def __str__(self):
		text = "{testo}"
		return text.format(testo = self.oggetto)
	
	class Meta:
		abstract = True

		
class ValidDate_a(models.Model):
	
	"""
	classe con i campi di data che registrano una validità temporale\n
	data_da: data di inizio\n
	data_a: data di fine\n
	"""
	
	data_da = models.DateField(
		_("Data inizio validità"),
		)
	data_a = models.DateField(
		_("Data fine validità"),
		null = True, blank = True,
		)

	class Meta:
		abstract = True


class Status_a(models.Model):
	
	"""
	classe con il solo campo di stato, standardizzato per convenienza\n
	stato: FK a tipologia nel sottoinsieme di tipo STATO\n
	"""
	
	stato = models.ForeignKey(
		"Tipologia",
		on_delete = models.PROTECT,
		verbose_name = _("Stato dell'elemento"),
		limit_choices_to = {'tipo' : STATO},
		default = 1,
		)

	class Meta:
		abstract = True	

		
class D3_a(models.Model):
	
	"""
	classe con i riferimenti al documentale; \n
	estrapolato dal testo generale nel caso in cui cambiasse il riferimento.\n
	id_documento: campo document_id di D.3\n
	"""
	
	id_documento = models.CharField(
		_("ID D.3 del documento collegato"),
		null = True, blank = True,
		)

	class Meta:
		abstract = True  

		
class RABS_a(models.Model):
	
	"""
	classe per i riferimenti alle RABS;\n
	estrapolato dal testo generale nel caso in cui cambiasse il riferimento.\n
	id_rabs: compo document_id in D:3 della RABS\n
	"""
	
	id_rabs = models.CharField(
		_("ID D.3 della RABS collegata"),
		null = True, blank = True,
		)

	class Meta:
		abstract = True



# classi funzionali

class Tema(Base_a):
	"""
	classe per trasportare il tema nei forms e nei template
	"""
	modello = models.CharField(_("Modello"), max_length=25, choices=modelli, unique=True,)
	tema = models.CharField('Tema', max_length=1, choices = temi)
	
	def __str__(self):
		return "{mod} -> {tem}".format(mod=self.modello, tem=self.tema)
	
	def get_tema(modello = ""):
		val = Tema.objects.filter(modello = modello.lower().capitalize() )
		if val.count() == 0:
			return ""
		else:
			return val[0].tema
	"""
	def segnalazione():
		s = Tema.objects.get(modello = modelli[SEGNALAZIONE])
		if s is None:
			return "a"
		else:
			return s.tema
	
	def intervento():
		s = Tema.objects.get(modello = modelli[INTERVENTO])
		if s is None:
			return "a"
		else:
			return s.tema
	
	def team():
		s = Tema.objects.get(modello = modelli[TEAM])
		if s is None:
			return "a"
		else:
			return s.tema
	
	def lavoro():
		s = Tema.objects.get(modello = modelli[LAVORO])
		if s is None:
			return "a"
		else:
			return s.tema
		
	def salva():
		s = Tema.objects.get(modello = modelli[SALVA])
		if s is None:
			return "a"
		else:
			return s.tema
	"""
	class Meta:
		verbose_name = "Tema"
		verbose_name_plural = "Temi"

	
class Vista(Base_a):
	
	"""
	Elenco delle viste selezionabili per ogni profilo
	"""
	
	nome = models.CharField(_("Nome della vista"), max_length = 80)
	nome_modello = models.CharField(_("Nome del Modello"), max_length = 30)
	
	def __str__(self):
		text = "{testo}"
		return text.format(testo = self.nome)

	class Meta:
		verbose_name = _("Vista")
		verbose_name_plural = _("Viste")


class Mansione(Base_a, ItDe_a, ):
	
	"""
	Elenco delle varie mansioni; necessaria per lo smistamento dei lavori.\n
	nessun campo specifico non ereditato.\n
	"""
	
	@classmethod 
	def urgente(self):
		res = self.objects.filter(translations__nome_breve = "Urgente")
		if res.count() == 0:
			a = self(
				nome_breve="Urgente",
				descrizione = "Mansione di soluzione interventi con carattere di urgenza",
			)
			a.save()
			for col in Collaboratore.objects.all():
				cm = CollaboratoreMansione(
					collaboratore = col,
					mansione = a,
					data_da = datetime.datetime.now(),
				)
				cm.save()
			return a
		else:
			return res[0]

			
   
   
   
   
	class Meta:
		verbose_name = _("Mansione")
		verbose_name_plural = _("Mansioni")

class MansioneTranslation(ItDe_aTranslation):
	master = models.ForeignKey(Mansione, related_name='translations', null=True, on_delete= models.PROTECT)


class Attivita(Base_a, ItDe_a, ):
	
	"""
	elenco delle attività dove incasellare i team di intervento.\n
	obbligo_foto: boolean per indicare se questa attività necessita di foto iniziale e finale\n
	chiusura_auto_lavoro: se false, il caposquadra deve verificare i lavori svolti\n
	tempo_stimato: valore indicativo in ore/uomo per svolgere il lavoro\n
	tempo_aumento: valore di giorni dopo il quale la priorità scala al livello successivo\n
	mansioni: m2m sulle mansioni che possono svolgere l'attività'\n
	"""
	
	obbligo_foto = models.BooleanField(
		_("Obbligo foto"),
		default = False,
		help_text = _("Se selezionato, impedisce di chiudere un lavoro se non sono caricate le foto iniziale e finale."),
		)
	chiusura_auto_lavoro = models.BooleanField(
		_("Chiusura automatica dei lavori"),
		default = False,
		help_text = _("Se selezionato, rende non obbligatoria la verifica del caposquadra per la chiusura dei lavori."),
		)
	tempo_stimato = models.IntegerField(
		_("Tempo stimato di soluzione"), 
		help_text = _("Il valore si intende indicato in ore/uomo"),
		)
	tempo_aumento = models.IntegerField(
		_("Tempo di aumento della priorità"), 
		help_text = _("Tempo dopo il quale la priorità aumenta di grado. Il valore si intende indicato in giornate"),
		)   
	mansioni = models.ManyToManyField(
		Mansione,
#		on_delete = models.PROTECT,
		verbose_name = _("Mansioni capaci di svolgere l'attività"),
		related_name = "attivita",
		)
	
	def collaboratori_validi(self, data=timezone.now()):
		coll_ids = [coll.id for coll in Collaboratore.objects.all() if coll.abile(self, data)==True]
		return Collaboratore.objects.filter(pk__in=coll_ids)

	@classmethod
	def urgente(self):
		res = self.objects.filter(translations__nome_breve="Urgente")
		if res.count() == 0:
			a = self(
				nome_breve = "Urgente",
				descrizione = "Attività relativa a lavoro con carattere di urgenza",
				obbligo_foto = False,
				tempo_stimato = 1,
				tempo_aumento = 1,
				colore = "#FF1B00",
				fa_visible = True,

				# mansioni = [Mansione.urgente(),], errato
			)
			a.save()
			a.mansioni.add(Mansione.urgente())
			a.save()
			return a
		else:
			return res[0]


	def __str__(self):
		text = "{nome} (TS:{ts} TA:{ta})"
		return text.format(nome = self.nome_breve, ts=self.tempo_stimato, ta=self.tempo_aumento)
	
	class Meta:
		verbose_name = _("Attività")
		verbose_name_plural = _("Attività")

class AttivitaTranslation(ItDe_aTranslation):
	master = models.ForeignKey(Attivita, related_name='translations', null=True, on_delete= models.PROTECT)


class Priorita(Base_a, ItDe_a):
	
	"""
	elenco di priorità standard, valorizzare con un numero intero\n
	valore: numero intero di indicizzazione delle priorità\n
	"""
	
	valore = models.IntegerField(
		_("Valore della Priorità"),
		)

	@property	
	def icona(self):
		tag = '<i class="{classe} icon_tt" style="color:{colore};float:right;"><span class="icon_text">&nbsp;{tipo}:&nbsp;{nome_breve}&nbsp;</span></i>'
		return tag.format(classe=self.fa_icon, colore=self.colore, tipo=_("Priorità"), nome_breve=self.nome_breve)
	
	def da_valore(val):
		pri = Priorita.objects.exclude(valore__gt = val).order_by('-valore')
		return pri[0]
	
	@classmethod
	def urgente(self):
		res = self.objects.filter(translations__nome_breve = "Urgente")
		if res.count() == 0:
			a = self(
				nome_breve = "Urgente",
				valore = 60, 
				descrizione = "Urgente",
				colore = "#FF1B00",
				fa_icon = "fa-solid fa-star",
				visible = True,
			)
			a.save()
			return a
		else:
			return res[0]

	class Meta:
		verbose_name = _("Priorità")
		verbose_name_plural = _("Priorità")

class PrioritaTranslation(ItDe_aTranslation):
	master = models.ForeignKey(Priorita, related_name='translations', null=True, on_delete= models.PROTECT)


class Anno(Base_a):
	
	"""
	classe che raccoglie gli anni di esercizio\n
	anno: stringa di 4 caratteri con l'anno'\n
	"""
	
	anno = models.CharField(
		_("Anno"), 
		max_length = 4, 
		)
	
	def __str__(self):
		text = "{yr} {testo}"
		return text.format(yr = _("Anno"), testo = self.anno)
	
	class Meta:
		verbose_name = _("Anno")
		verbose_name_plural = _("Anni")


class Squadra(Base_a, ItDe_a):
	
	"""
	Classe che definisce una squadra di collaboratori.\n
	Nessun campo non ereditato.\n
	"""
	
	def set_id_mansioni(self, data=timezone.now):
		data = call(data)
		mans = set(())
		for col in self.collaboratore_set.all():
			for man in col.collaboratoremansione_set.all().exclude(data_da__gt = data).exclude(data_a__lt  = data):
				mans.add(man.mansione.id)
		return mans
	
	def interventi(self, data=timezone.now):
		data = call(data)
		return Intervento.objects.all().filter(team__attivita__mansioni__id__in = self.set_id_mansioni(data))

	class Meta:
		verbose_name = _("Squadra")
		verbose_name_plural = _("Squadre")

class SquadraTranslation(ItDe_aTranslation):
	master = models.ForeignKey(Squadra, related_name='translations', null=True, on_delete= models.PROTECT)


class Tipologia (Base_a, ItDe_a):
	
	"""
	classe che racchiude tutte le tipologie, raggruppare con l'enum "tipologie"\n
	tipo: scleta del tipo di tipologia, legata all'enum "tipologie"\n
	abbreviazione: abbreviazione del tipo specifico, di tre lettere\n
	"""
	
	tipo = models.CharField(
		_("Tipo"),
		max_length = 2,
		choices = tipologie
		)
	abbreviazione = models.CharField(
		_("Abbreviazione"),
		max_length = 3,
		)
	ordine = models.IntegerField(
		verbose_name = _("Ordine"),
		default = 1,
		)
	
	def __str__(self):
		text = "{nome} ({sigla}-{abbr})"
		return text.format(
			nome = self.nome_breve,
			sigla = self.tipo,
			abbr = self.abbreviazione,
			)
	
	@classmethod
	def elenco_tipo(self, tipo):
		return self.objects.filter(tipo = tipo)
	
	@classmethod
	def foto(self):
		return self.elenco_tipo(FOTO)
	
	@classmethod
	def stati(self):
		return self.elenco_tipo(STATO)
	
	@classmethod
	def assenze(self):
		return self.elenco_tipo(ASSENZA)
	
	@classmethod
	def reperibilita(self):
		return self.elenco_tipo(REPERIBILITA) 
	
	@classmethod
	def origini_segnalazione(self):
		return self.elenco_tipo(SEGNORIG)
	
	@classmethod
	def tipi_segnalazione(self):
		return self.elenco_tipo(SEGNTIPO)
	
	@classmethod
	def tipologia(self, tipo, abbreviazione):
		res = None 
		a = self.elenco_tipo(tipo).filter(abbreviazione = abbreviazione)
		if a.count() == 0:
			res = self(tipo=tipo, 
				   abbreviazione=abbreviazione, 
				   colore="#000000", 
				   ordine=1, 
				   nome_breve="Nuovo inserimento: {t}-{a}".format(t=tipo, a=abbreviazione), 
				   descrizione="Nuovo inserimento: {t}-{a}".format(t= tipo, a=abbreviazione),
			)
			res.save()
		else:
			res = a[0]
		return res
	
	@classmethod
	def t_stato(self, abbr):
		return self.tipologia(tipo = STATO, abbreviazione=abbr)
	
	@property	
	def icona(self):
		tag = '<i class="{classe} icon_tt" style="color:{colore};float:right;"><span class="icon_text">&nbsp;{tipo}:&nbsp;{nome_breve}&nbsp;</span></i>'
		return tag.format(classe=self.fa_icon, colore=self.colore, tipo=tipologie[self.tipo], nome_breve=self.nome_breve)
	
	
	class Meta:
		verbose_name = _("Tipologia")
		verbose_name_plural = _("Tipologie")
		unique_together = ["tipo", "abbreviazione"]

class TipologiaTranslation(ItDe_aTranslation):
	master = models.ForeignKey(Tipologia, related_name='translations', null=True, on_delete= models.PROTECT)


class Collaboratore(Base_a):
	
	"""
	classe che raggruppa i collaboratori del progetto.\n
	dipendente: fk a dipendenti.Dipendente, per collegare utente e diritti\n
	squadra: fk a Squadra, per assegnarlo ad una squadra operativa\n
	telefono: per segnare un cellularei di riferimento\n
	responsabile: boolean per indicare se un collaboratore sia o meno responsabile di struttura\n
	mansioni: m2m per le mansioni per cui è accreditato\n
	assenze: m2m per periodi di assenza\n
	reperibilita: m2 per periodi di reperibilità \n
	"""
	
	dipendente = models.OneToOneField(
		Dipendente, 
		on_delete = models.PROTECT,
		verbose_name = _("Dipendente collegato"),
		)
	squadra = models.ForeignKey(
		Squadra, 
		on_delete = models.PROTECT, 
		verbose_name = _("Squadra"),
		)
	telefono = models.CharField(
		_("Telefono"), 
		max_length = 15, 
		)
	responsabile = models.BooleanField(
		_("Responsabile di strutture"), 
		default = False,
		)
	mansioni = models.ManyToManyField(
		Mansione,
		verbose_name = _("Mansioni assegnate"),
		through = "CollaboratoreMansione",
		related_name = "collaboratori"
		)
	assenze = models.ManyToManyField(
		Tipologia,
		verbose_name = _("Periodi di assenza"),
		through = "CollaboratoreAssenza",
		related_name = "collaboratori_assenze"
		)
	reperibilita = models.ManyToManyField(
		Tipologia,
		verbose_name = _("Periodi di reperibilità"),
		through = "CollaboratoreReperibilita",
		related_name = "collaboratori_reperibilita"
		)
	sigla = models.CharField(
		_("Sigla"), 
#		default="XXX", 
		max_length=3,
		unique=True,
		)
	vista = models.ForeignKey(
		Vista,
		verbose_name = "Vista iniziale",
		default = 2,
		on_delete = models.CASCADE,
		)
	
	def __str__(self):
		text = "{cognome} {nome}"
		return text.format(
			cognome = self.dipendente.cognome.upper(),
			nome = self.dipendente.nome,
			)
	
	def mansioni_attive(self, data=timezone.now()):
		id_mans = self.collaboratoremansione_set.exclude(data_da__gt=data).exclude(data_a__lt=data).values_list("mansione", flat=True)
		return Mansione.objects.filter(pk__in=id_mans)
	
	def abile(self, attivita, data=timezone.now()):
		res = False
		if attivita is None:
			res = False
		else:
			qs_att = attivita.mansioni.all()
			qs_coll = self.mansioni_attive(data=data)
			qs= qs_att.intersection(qs_coll)
			if qs.count() >0:
				res = True
		return res
	
	def qs_reperibile(self, data=timezone.now):
		data=call(data)
		return CollaboratoreReperibilita.objects.filter(collaboratore=self.id).exclude(data_da__gt=data).exclude(data_a__lt=data)
	
	def qs_assente(self, data=timezone.now):
		data=call(data)
		return CollaboratoreAssenza.objects.filter(collaboratore=self.id).exclude(data_da__gt=data).exclude(data_a__lt=data)
	
	def lavori_da_svolgere(self, data=timezone.now):
		data=call(data)
		return Lavoro.lavori_da_svolgere(collaboratore=self, data=data, pianificati=False)
	
	def lavori_pianificati(self, data=timezone.now):
		data=call(data)
		return Lavoro.lavori_da_svolgere(collaboratore=self, data=data, pianificati=True)
	
	def tempolavoro_attivo(self, data=timezone.now):
		data=call(data)
		lavori = Lavoro.objects.filter(collaboratore=self, team__intervento__data_esecuzione__lte = data)
		result = None
		for lav in lavori:
			tp = lav.tempilavoro_set.exclude(inizio__gt=data).exclude(fine__lt=data)
			if tp.count()>0:
				result = tp[0]
		return result
	
	def lavoro_attivo(self, data=timezone.now):
		data=call(data)
		tlav = self.tempolavoro_attivo(data=data)
		if tlav is None:
			return None
		else:
			return tlav.lavoro
		
	def lavorando(self, data=timezone.now):
		data=call(data)
		tlav = self.tempolavoro_attivo(data=data)
		if tlav is None:
			return False
		else:
			return True
		
	
	class Meta:
		verbose_name = _("Collaboratore")
		verbose_name_plural = _("Collaboratori")
		order_with_respect_to = "dipendente"


class CdC (Base_a,ItDe_a):
	
	"""
	Classe che raccoglie i centri di costo relativi alle strutture.\n
	note: annotazioni relative ai centri di costo.\n
	"""
	
	note = models.TextField(
		_("Annotazioni"),
		null = True, blank = True,
		)

	class Meta:
		verbose_name = _("Centro di costo")
		verbose_name_plural = _("Centri di costo")

class CdCTranslation(ItDe_aTranslation):
	master = models.ForeignKey(CdC, related_name='translations', null=True, on_delete= models.PROTECT)


class Struttura(Base_a, ItDe_a):
	
	"""
	tabella che contiene i dati di struttura, anche ointesa in senso lato, es: rete stradale.\n
	responsabile: FK a collaboratori filtrati per responsabile=True, che indica chi sia il responsabile di struttura\n
	cdc: fk a CdC per indicare il centro di costo relativo alla struttura\n
	indirizzo_it e _de: indirizzi in italiano e tedesco della struttura\n
	telefono: nimero di telefono di riferimento della struttura.\n
	"""
		
	responsabile = models.ForeignKey(
		Collaboratore,
		on_delete = models.PROTECT,
		verbose_name = _("Responsabile di struttura"),
		limit_choices_to = {'responsabile': True},
		)
	cdc = models.ForeignKey(
		CdC,
		on_delete = models.PROTECT,
		verbose_name = _("Centro di costo"),
		)
	indirizzo = TranslatedField()
	telefono = models.CharField(
		_("Numero di telefono"),
		max_length = 15,
		)
	autorizzati = models.ManyToManyField(
		Servizio,
		related_name = "strutture", 

	)	
 
 
	class Meta:
		verbose_name = _("Struttura")
		verbose_name_plural = _("Strutture")

class StrutturaTranslation(ItDe_aTranslation):
	master = models.ForeignKey(Struttura, related_name='translations', null=True, on_delete= models.PROTECT)
	indirizzo = models.CharField(
		_("Indirizzo"),
		max_length = 150,
		)


class Diritto(Base_a):
	nome = models.CharField(_("Nome del diritto"), max_length = 15)
	capocantiere = models.BooleanField(_("Capocantiere"), default=False)
	caposquadra = models.BooleanField(_("Caposquadra"), default=False)
	coordinatore = models.BooleanField(_("Coordinatore"), default=False)
	operaio = models.BooleanField(_("Operaio"), default=False)
	struttura = models.BooleanField(_("Referente di struttura"), default=False)
	ufficio = models.BooleanField(_("Ufficio"), default=False)
	
	def __str__(self):
		return self.nome
	
	class Meta:
		verbose_name = "Diritto"
		verbose_name_plural = "Diritti"
	
	def dict_diritti(collaboratore):
		usr = collaboratore.dipendente.user
		res = {}
		diritti = Diritto.objects.all()
		for dr in diritti:
			res[dr.nome]=False
			for key, value in ruoli.items():
				if usr.groups.filter(name = key).count() >0:
					res[dr.nome] |= getattr(dr, value)	
		return res
	
		

# classi operative



class Evento(Base_a, ItDe_a):
	
	"""
	Classe che agisce da contenitore e classificazione delle segnalazioni.\n
	nessun campo non ereditato.\n
	"""

	
	pass
	class Meta:
		verbose_name = _("Evento")
		verbose_name_plural = _("Eventi")
  
	@classmethod
	def default(self):
		res = None 
		a = self.objects.filter(id = 0)
		if a.count() == 0:
			res = self( 
				   id=0,
				   colore="#555555",  
				   nome_breve="Nessun Evento", 
				   descrizione="Nessun evento selezionato",
				   fa_icon="fa-solid fa-square",
				   fa_visible=False,
			)
			res.save()
		else:
			res = a[0]
		return res

class Tag(Evento):
	
	"""
	Classe proxy di Evento che agisce da hashtag delle segnalazioni.\n
	nessun campo non ereditato.\n
	"""
	
	@property	
	def icona(self):
		tag = '<i class="{classe} icon_tt" style="color:{colore};float:right;"><span class="icon_text">&nbsp;{tipo}:&nbsp;{nome_breve}&nbsp;</span></i>'
		return tag.format(classe=self.fa_icon, colore=self.colore, tipo=_("Tag Evento"), nome_breve=self.nome_breve)
	
	class Meta:
		proxy = True
		verbose_name = _("Tag")
		verbose_name_plural = _("Tags")

class EventoTranslation(ItDe_aTranslation):
	master = models.ForeignKey(Evento, related_name='translations', null=True, on_delete= models.PROTECT)


class Segnalazione(Base_a, Periodic_a, Description_a, Status_a, D3_a):
	
	"""
	Classe atta a contenere tutti i dati relativi ad una segnalazione di intervento.\n
	data_pianificazione: data di pianificazione della soluzione\n
	struttura: fk a strutture per identificare il luogo di intervento\n
	origine: fk a tipologia su SEGNORIG per indicare da dove provenga la segnalazione\n
	segnalatore: nome e cognome della persona segnalante\n
	email: indirizzo e-mail del segnalatore; se valorizzato, invia automaticamente una risposta quando chiusa.\n
	telefono: numero di telefono del segnalatore\n
	risposta: testo della risposta alla segnalazione da inviare un avolta conclusa.\n
	eventi: M2M per Evento, collega la segnalazione ad uno o più eventi (annui)\n
	tipo: fk a tipologia su SEGNTIPO per indicare la tipologia di segnalazione\n
	"""
	
	data_pianificazione = models.DateField(
		_("Data di pianificazione"),
#		null=True, blank=True,
#		help_text = _("Inserire la data a partire dalal quale la pianificazione può avvenire")
		)
	struttura = models.ForeignKey(
		Struttura,
		on_delete = models.PROTECT,
		verbose_name = _("Struttura di riferimento"),
		)
	origine = models.ForeignKey(
		Tipologia,
		on_delete = models.PROTECT,
		verbose_name = _("Origine della segnalazione"),
		related_name = "origine_segnalazioni",
		limit_choices_to = {'tipo' : SEGNORIG},
		)
	segnalatore = models.CharField(
		_("Nome e cognome del segnalatore"), 
		max_length = 250,
		)
	email = models.EmailField(
		_("E-mail della segnalazione"),
		help_text = _("Se valorizata, la chiusura della segnalazione invia una risposta."),
		null = True, blank = True,
		)
	telefono = models.CharField(
		_("Telefono del segnalatore"),
		max_length = 15,
		null = True, blank = True, 
		)
	risposta = models.TextField(
		_("Risposta alla segnalazione"),
		null = True, blank = True,
		)
	eventi = models.ManyToManyField(
		Evento,
		verbose_name = _("Eventi collegati"),
		related_name = "evento_segnalazioni",
		through = "EventoSegnalazione",
		null = True, blank = True,
		)
	tags = models.ManyToManyField(
		Tag,
		verbose_name = _("Tag collegati"),
		related_name = "tag_segnalazioni",
		null = True, blank = True,
		)
	tipo = models.ForeignKey(
		Tipologia,
		on_delete = models.PROTECT,
		verbose_name = _("Tipo di segnalazione"),
		related_name = "tipo_segnalazioni",
		limit_choices_to = {'tipo' : SEGNTIPO},
		)
	
	def duplica(self):
		if self.periodico:
			a = copy.deepcopy(self)
			a.id = None
			if a.periodo:
				a.id = None 
				a.data_pianificazione += datetime.timedelta(days=a.periodo)
				if a.cicli:
					a.cicli -= 1 
					if a.cicli <= 0:
						a.cicli = None
						a.periodico = None
				if a.duplicare:
					for itv in self.intervento_set.all():
						itv.duplica(a)
			a.save()
		pass
	
	def conta_lavori(self):
		tot = 0
		for itv in self.intervento_set.all():
			tot += itv.conta_lavori()
		return tot
	
	def conta_teams(self):
		tot = 0
		for itv in self.intervento_set.all():
			tot += itv.conta_teams()
		return tot
	
	def calcola_stato(self):
		"""
		assegna lo stato alla segnalazione in base agli stati degli interventi
		"""
		verificato = Tipologia.tipologia(STATO, "VER")
		assegnato = Tipologia.tipologia(STATO, "ASS")
		acquisito = Tipologia.tipologia(STATO, "ACQ")
		in_corso = Tipologia.tipologia(STATO, "INC")
		in_pausa = Tipologia.tipologia(STATO, "PAU")
		chiuso = Tipologia.tipologia(STATO, "CHI")

		stato_r = acquisito

		if self.intervento_set.all().count() == 0:
			stato_r = acquisito   
		else:
			ass = self.intervento_set.filter(stato = assegnato).count()
			acq = self.intervento_set.filter(stato = acquisito).count()
			inc = self.intervento_set.filter(stato = in_corso).count()
			pau = self.intervento_set.filter(stato = in_pausa).count()
			ver = self.intervento_set.filter(stato = verificato).count()
			# chi = self.intervento_set.filter(stato = chiuso).count()
			tot = self.intervento_set.all().count()

			if pau > 0:
				stato_r = in_pausa
			elif inc > 0:
				stato_r = in_corso
			elif acq > 0: 
				stato_r = acquisito
			elif ass > 0:
				stato_r = assegnato
			elif ver == tot:
				stato_r == verificato
			else:
				stato_r == chiuso
		return stato_r		

		
 
	def save(self, *args, **kwargs):
		acquisito = Tipologia.tipologia(STATO, "ACQ")
		verificato = Tipologia.tipologia(STATO, "VER")

		
		if not self.id:
			self.stato = acquisito
		if self.stato == verificato:
			try:
				sg = Segnalazione.objects.get(pk=self.id)
				if sg.stato != verificato:
					self.duplica()
			except Segnalazione.DoesNotExist:
				self.duplica()
		return super(Segnalazione, self).save(*args, **kwargs)
	
	class Meta:
		verbose_name = _("Segnalazione")
		verbose_name_plural = _("Segnalazioni")
		indexes = [ 
             models.Index(fields = ['stato', ]), 
             models.Index(fields = ['struttura', ]),
             ]


class Intervento(Base_a, Periodic_a, Description_a, Status_a, RABS_a):
	
	"""
	classe per raccogliere i dati degli interventi.\n
	segnalazione: fk a Segnalazione per collegare intervento ad eventuale segnalazione\n
	struttura: fk a struttura opzionale per identificare la struttura in caso di segnalazione assente\n
	priorita: fk a priorita per impostare la priorità iniziale dell'intervento\n
	preposto: fk a collaboratore, per indicare chi sia l'operaio preposto all'intervento\n
	precedente: pk a Intervento per indicare l'intervento che lo precede logicamwnte (intervento di origine di questo)\n
	data_visibilita: l'intervento sarà visibile in interfaccia a partie dalla data indicata\n
	data_urgente: l'intervento avrà la massima urgenza a decorrere da questa data\n
	data_esecuzione: l'intervento potrà essere eseguibile a partire dalla data indicata\n
	provvisorio: l'intervento è provvisorio, ovvero da completare\n
	"""
	
	segnalazione = models.ForeignKey(
		Segnalazione,
		on_delete = models.CASCADE, 
		verbose_name = _("Segnalazione relativa"),
		null = True, blank = True,
		)
	struttura = models.ForeignKey(
		Struttura,
		on_delete = models.PROTECT,
		verbose_name = _("Struttura di riferimento"),
		null = True, blank = True,
		)
	priorita = models.ForeignKey(
		Priorita, 
		on_delete = models.PROTECT, 
		verbose_name = _("Priorità iniziale"),
		)
	preposto = models.ForeignKey(
		Collaboratore,
		on_delete = models.PROTECT,
		verbose_name = _("Preposto all'intervento"),
		)
	precedente = models.ForeignKey(
		"Intervento",
		on_delete = models.PROTECT,
		verbose_name = _("Intervento precedente"),
		null = True, blank = True,
		)
	data_visibilita = models.DateField(
		_("Data di visibilità"),
		default = datetime.datetime.now,
		help_text = _("Data a partire dalla quale l'intervento diventa visibile."),
		)
	data_urgente = models.DateField(
		_("Data di urgenza"),
		help_text = _("Data a partire dalla quale l'intervento diventa urgente."),
		null = True, blank = True,
		)
	data_esecuzione = models.DateField(
		_("Data di esecuzione"),
		default = datetime.datetime.now,
		help_text = _("Data a partire dalla quale l'intervento può venire risolto."),
		) 
	provvisorio = models.BooleanField(
		_("Intervento provvisorio"),
		default = False, 
		help_text = _("Intervento incompleto inserito da sistema"), 
		)

	
	@property
	def foto_istruzioni(self):
		istruzioni = Tipologia.tipologia(FOTO, 'IST')
		return self.foto_set.filter(tipologia=istruzioni)
	
	
	def duplica(self, seg = None):
		a = copy.deepcopy(self)
		verificato = Tipologia.tipologia(STATO, "VER") 
		if a.periodico:
			a.id = None
			if seg:
				a.segnalazione = seg
				if seg.periodico and seg.duplicare:
					a.data_visibilita += datetime.timedelta(days=a.segnalazione.periodo)
				elif a.stato == verificato:
					a.data_visibilita += datetime.timedelta(days=a.periodo)
					a.cicli -= 1
					if a.cicli <= 0:
						a.cicli = None
						a.periodico = False
			else:
				a.data_visibilita += datetime.timedelta(days=a.periodo)
				a.cicli -= 1
				if a.cicli <= 0:
					a.cicli = None
					a.periodico = False
			a.save()	
			if a.duplicare:
				for tm in self.team_set.all():
					t = copy.deepcopy(tm)
					t.id = None
					t.intervento = a
					t.save()
					for lv in tm.lavoro_set.all():
						l = copy.deepcopy(lv)
						l.id = None
						l.team = t
						l.save()
		pass				
			

	def conta_teams(self):
		return self.team_set.count()
	
	def conta_lavori(self):
		tot = 0
		for tm in self.team_set.all():
			tot += tm.conta_lavori()
		return tot

	def calcola_stato(self):
		"""
		assegna lo stato all'intervento in base agli stati dei lavori
		"""
		acquisito = Tipologia.tipologia(STATO, "ACQ")
		assegnato = Tipologia.tipologia(STATO, "ASS")
		chiuso = Tipologia.tipologia(STATO, "CHI")
		verificato = Tipologia.tipologia(STATO, "VER")
		in_corso = Tipologia.tipologia(STATO, "COR")
		in_pausa = Tipologia.tipologia(STATO, "PAU")

		stato_r = assegnato
  
		tot = self.conta_lavori()
  
		if tot == 0:
			stato_r = acquisito
		else:
			lavs = Lavoro.objects.filter(team__intervento=self.id)
			ass = lavs.filter(stato = assegnato).count()
			# acq = lavs.filter(stato = acquisito).count()
			inc = lavs.filter(stato = in_corso).count()
			pau = lavs.filter(stato = in_pausa).count()
			ver = lavs.filter(stato = verificato).count()
			# chi = lavs.filter(stato = chiuso).count()

			if pau > 0:
				stato_r = in_pausa
			elif inc > 0:
				stato_r = in_corso
			elif ass > 0:
				stato_r = assegnato
			elif ver == tot:
				stato_r = verificato
			else:
				stato_r = chiuso
		return stato_r


			
			
 
	def save(self, *args, **kwargs):
		
		acquisito = Tipologia.tipologia(STATO, "ACQ")
		# assegnato = Tipologia.tipologia(STATO, "ASS")
		# chiuso = Tipologia.tipologia(STATO, "CHI")
		verificato = Tipologia.tipologia(STATO, "VER")
		# in_corso = Tipologia.tipologia(STATO, "COR")
		
		if not self.id:
			self.stato = acquisito
		# else:
		# 	if self.segnalazione:
		# 		if self.stato in (assegnato, chiuso, verificato):
		# 			res = True
		# 			for i in self.segnalazione.intervento_set.all():
		# 				res &= (i.stato == self.stato)
		# 			if res:
		# 				self.segnalazione.stato = self.stato
		# 				self.segnalazione.save()
		# 		elif self.stato == in_corso:
		# 			self.segnalazione.stato = self.stato
		# 			self.segnalazione.save()
		if self.stato == verificato:
			try:
				intv = Intervento.objects.get(pk=self.id)
				if intv.stato != verificato:
					self.duplica()
			except Intervento.DoesNotExist:
				self.duplica()
		res = super(Intervento, self).save(*args, **kwargs)
		if self.segnalazione:
			self.segnalazione.stato = self.calcola_stato()
			self.segnalazione.save()
		return res

	class Meta:
		verbose_name = _("Intervento")
		verbose_name_plural = _("Interventi")
		indexes = [ 
             models.Index(fields = ['stato', ]), 
             models.Index(fields = ['struttura', ]),
             models.Index(fields = ['segnalazione', ]),
             ]


class TeamQueryset(models.QuerySet):
	def effettivi(self):

		day_1 = datetime.timedelta(days=1)

		return self.annotate(
			attesa_c =  EW((timezone.now().date() - F('intervento__data_esecuzione')), models.DurationField()),
			aumento_c = Case(When(tempo_aumento__isnull=True, then= EW(day_1 * F('attivita__tempo_aumento'), models.DurationField())), default=EW(day_1 * F('tempo_aumento'), models.DurationField()))
			)
	

class Team(Base_a):
	
	"""
	Classe atta a raccoglere i dati relativi ad un team di intervento di risoluzione di un intervento.\n
	intervento: FK ad Intervento per collegarlo all'intervento relativo\n
	attivita: tipologia di attività da svolgere dal team\n
	tempo_stimato: tempo stimato di soluzione dell'intervento per il team, in ore uomo. \n
		Il valore sovrascrive quello dell'attività, se impostato.\n
	tempo_aumento: tempo dopo il quale la priorità dell'intervento sale di urgenza.\n
		Il valore sovrascrive quello dell'attività, se impostato.\n
	"""
	
	objects = TeamQueryset.as_manager()
	
	intervento = models.ForeignKey(
			Intervento,
			on_delete = models.CASCADE, 
			verbose_name = _("Intervento collegato"),
			)
	attivita = models.ForeignKey(
			Attivita,
			on_delete = models.CASCADE, 
			verbose_name = _("Attività coinvolta"),
			)
	tempo_stimato = models.IntegerField(
		_("Tempo stimato di soluzione"), 
		help_text = _("Il valore si intende indicato in ore/uomo. Se non impostato equivale al TS dell'attività."),
		null=True, blank=True,
		)
	tempo_aumento = models.IntegerField(
		_("Tempo di aumento della priorità"), 
		help_text = _("Tempo dopo il quale la priorità aumenta di grado. Il valore si intende indicato in giornate. Se non impostato equivale al TA dell'attività."),
		null=True, blank=True,
		)

	def __str__(self):
		text = "{att} (TS:{ts} TA:{ta})"
		ts_eff = self.attivita.tempo_stimato
		ta_eff = self.attivita.tempo_aumento
		if self.tempo_stimato:
			ts_eff = self.tempo_stimato
		if self.tempo_aumento:
			ta_eff = self.tempo_aumento
		return text.format(
			att = self.attivita.nome_breve,
			ts = ts_eff,
			ta = ta_eff,
			)
	
	@property
	def attesa(self):
		obj = Team.objects.effettivi().get(pk=self.id)
		return max(obj.attesa_c, datetime.timedelta(0))
	
	@property
	def aumento(self):
		obj = Team.objects.effettivi().get(pk=self.id)
		return obj.aumento_c
	
	@property
	def val_priorita(self):
		return self.intervento.priorita.valore + (self.attesa // self.aumento) * INT_PRIORITA
	
	@property
	def priorita(self):
		return Priorita.da_valore(self.val_priorita)
	
	
 
	def conta_lavori(self):
		return self.lavoro_set.count()
	
	
	
	class Meta:
		verbose_name = _("Team di intervento")
		verbose_name_plural = _("Teams di intervento")
		indexes = [ 
             models.Index(fields = ['intervento', ]), 
             models.Index(fields = ['attivita', ]),
             ]



class Foto(Gis_a):
	
	"""
	Classe atta a contenere le foto effettuate dagl operai in sede di lavoro.\n
	tipoogia: fk a Tipologia su FOTO, indica se la foto È iniziale, finale o in corso d'opera\n
	intervento: fk a Intervento per indicare a quale intervento sia collegata.\n
	collaboratore: fk a Collaboratore che iundica chi sia l'autore della foto\n
	foto: imagefield con l'immagine relativa\n
	posizione: punto geografico che geolocalizza la foto\n
	note: annotazioni in merito alla foto.\n
	"""
	
	tipologia = models.ForeignKey(
		Tipologia,
		on_delete = models.PROTECT,
		verbose_name = _("Tipo di foto"),
		related_name = "foto_tipo",
		limit_choices_to = {'tipo' : FOTO},
		) 
	intervento = models.ForeignKey(
			Intervento,
			on_delete = models.CASCADE, 
			verbose_name = _("Intervento collegato"),
			)
	collaboratore = models.ForeignKey(
		Collaboratore,
		on_delete = models.PROTECT,
		verbose_name = _("Collaboratore che inserisce la foto"),
		)
	foto = models.ImageField(upload_to = "foto/%Y/%m/")
	posizione = models.PointField(null=True, blank=True, )
	note = models.TextField(
		_("Note"),
		null = True,
		blank = True,
		)
	
	def __str__(self):
		text = "{tipo}: {interv} - {collab}"
		return text.format(
			interv = self.intervento, 
			collab = self.collaboratore.dipendente.cognome,
			tipo = self.tipologia.abbreviazione
			)
	
	class Meta:
		verbose_name = _("Foto")
		verbose_name_plural = _("Foto")


class Lavoro(Base_a, Description_a, Status_a):
	
	"""
	Classe adita a contenere i dati relativi ad un lavoro assegnato\n
	collaboratore: fk a Collaboratore, per indicare a quale operaio venga assegnato il lavoro\n
	team: fk a Team per capire quale team d'intervento venga assegnato\n
	durata_prevista: ore-uomo di lavoro previsto\n
	caposquadra: id del caposwquadra che verifica il lavoro (se richiesto)\n
	accessorio: boolean che se vero, indica che il lavoro È accessorio all'intervento\n
	urgenza: lavoro svolto in carattere di urgenza\n
	mod_priorita: modifica manuale della priorità del lavoro.\n
	"""
	
	collaboratore = models.ForeignKey(
		Collaboratore,
		on_delete = models.PROTECT,
		verbose_name = _("Collaboratore incaricato"),
		)
	team = models.ForeignKey(
		Team,
		on_delete = models.PROTECT,
		verbose_name = _("Team di intervento collegato"),
		)
	durata_prevista = models.DecimalField(
		_("Durata prevista"),
		help_text = _("Il dato è inserito in ore/uomo."),
		max_digits = 6,
		decimal_places = 2,		
		)	
	caposquadra = models.ForeignKey(
		Collaboratore,
		on_delete = models.PROTECT,
		verbose_name = _("Caposquadra che ha verificato"),
		related_name = "lavoro_approvato",
		null = True,
		blank = True,
		)
	accessorio = models.BooleanField(
		_("Lavoro Accessorio"),
		default = False,
		)
	urgenza = models.BooleanField(
		_("Lavoro inserito con carattere di urgenza"),
		default = False,
		)
	mod_priorita = models.IntegerField(
		_("Modifica manuale della priorità"),
		default = 0,
		)
	
	
	@property
	def attivo(self):
		tl = self.tempilavoro_set.exclude(inizio__gt=timezone.now()).exclude(fine__lt=timezone.now())
		if tl.count() == 0:
			return False
		else:
			return True
	
	@property
	def tl_attivo(self):
		if self.attivo:
			return self.tempilavoro_set.exclude(inizio__gt=timezone.now()).exclude(fine__lt=timezone.now())[0]
		else:
			return None
	
	@property
	@admin.display(
			description = _('Priorità totale'),
			boolean=False ,
	#		ordering = 'team__val_priorita',
		)
	def val_priorita(self):
		return self.team.val_priorita + self.mod_priorita
		
	@property
	def priorita(self):
		return Priorita.da_valore(self.val_priorita)
	
	@classmethod
	def stati(*args):
		return Tipologia.objects.filter(tipo=STATO).order_by('ordine')
	
	@classmethod
	def lavori_da_svolgere(self, collaboratore, data=timezone.now, pianificati=False, ordinati=True):
		data=call(data)
		chiuso = Tipologia.tipologia(STATO, "CHI")
		verificato = Tipologia.tipologia(STATO, "VER")
		lav_tot = self.objects.exclude(stato__in=(chiuso, verificato)).filter(
			collaboratore=collaboratore,
			team__intervento__data_visibilita__lte=data
			)
		lv_res = None
		if pianificati:
			lv_res = lav_tot.filter(team__intervento__data_esecuzione__gt=timezone.now())
		
		else:
			lv_res = lav_tot.filter(team__intervento__data_esecuzione__lte=timezone.now())
		if ordinati:
			return sorted(lv_res, key=lambda p: -p.val_priorita)
		else:
			return lv_res
		
	
	@property
	def da_fare(self):
		chiuso = Tipologia.tipologia(STATO, "CHI")
		verificato = Tipologia.tipologia(STATO, "VER")
		if self.stato in (chiuso, verificato):
			return False
		else:
			return True

	@property
	def tempo_totale(self):
		tot = datetime.timedelta(0)
		for tlv in self.tempilavoro_set.all():
			if tlv.fine:
				tot += tlv.fine - tlv.inizio
		return tot

	@property
	def tempo_totale_h(self):
		humanize.i18n.activate("it_IT")
		return humanize.precisedelta(self.tempo_totale)

	@property
	def minuti_totali(self):
		return  int(self.tempo_totale.total_seconds() // 60)

	@property 
	def tempo_umanizzato(self):
		t = humanize.i18n.activate("it_IT")
		return humanize.precisedelta(self.tempo_totale)
	
	
	@property
	def csv_row(self):
		sep = ";"
		row = ""
		row += self.oggetto + sep
		row += self.descrizione + sep
		row += self.collaboratore.__str__() + sep
		row += "{d}".format(d=self.tempilavoro_set.aggregate(Min("inizio"))["inizio__min"]) + sep
		row += "{d}".format(d=self.tempilavoro_set.aggregate(Max("fine"))["fine__max"]) + sep
		row += self.stato.__str__() + sep
		row += "{n}".format(n=self.minuti_totali) + sep
		row += "{n}".format(n=self.team.intervento.segnalazione.allegato_set.count()) + sep
		row += "{n}".format(n=self.team.intervento.foto_set.count()) + sep
		row += "{d}".format(d=self.attivo) + sep
		row += "{n}".format(n=self.team.intervento.id) + sep
		row += self.team.intervento.oggetto + sep
		row += self.team.attivita.__str__() + sep
		row += "{d}".format(d=self.team.intervento.segnalazione.data_creazione) + sep
		row += self.team.intervento.segnalazione.struttura.__str__() + sep
		row += self.team.intervento.segnalazione.segnalatore.__str__() + sep
		row += self.team.intervento.segnalazione.struttura.cdc.__str__() + sep
		row += "{n}".format(n=self.team.intervento.segnalazione.id) + sep
		row += self.team.intervento.segnalazione.oggetto + sep
		row += self.team.intervento.segnalazione.tipo.__str__() + sep
		for tg in self.team.intervento.segnalazione.tags.all():
			row += tg.nome_breve + "|"
		return row

	@classmethod
	def csv_intestazione(self):
		row = ""
		sep = ";"
		row += _("Oggetto") + sep
		row += _("Descrizione") + sep
		row += _("Incaricato") + sep
		row += _("Prima attività") + sep
		row += _("Ultima attività") + sep
		row += _("Stato del lavoro") + sep
		row += _("Tempo totale") + sep
		row += _("Allegati") + sep
		row += _("Foto") + sep
		row += _("Attivo") + sep
		row += _("ID intervento") + sep
		row += _("Oggetto intervento") + sep
		row += _("Team di intervento") + sep
		row += _("Data segnalazione") + sep
		row += _("Struttura") + sep
		row += _("Segnalatore") + sep
		row += _("CdC") + sep
		row += _("ID Segnalazione") + sep
		row += _("Oggetto segnalazione") + sep
		row += _("Tipo segnalazione") + sep
		row += _("Tags") + sep
		return row

	@classmethod
	def lavori_data(self):
		return self.objects.annotate(data_inizio=Min("tempilavoro__inizio")).annotate(data_fine=Max("tempilavoro__fine"))
	
	def collaboratori(*args):
		return Collaboratore.objects.all().order_by('dipendente__cognome', 'dipendente__nome')
	
	def save(self, *args, **kwargs):
		assegnato = Tipologia.tipologia(STATO, "ASS")
		# chiuso = Tipologia.tipologia(STATO, "CHI")
		# verificato = Tipologia.tipologia(STATO, "VER")
		# in_corso = Tipologia.tipologia(STATO, "COR")
		
		if not self.id:
			self.stato = assegnato
		# 	res = True
		# 	for t in self.team.intervento.team_set.all():
		# 		res &= (t.lavoro_set.all().count()>0)
		# 		if res:
		# 			self.team.intervento.stato = assegnato
		# 			self.team.intervento.save()
		# else:
		# 	if self.stato in (chiuso, verificato):
		# 		res = True
		# 		for t in self.team.intervento.team_set.all():
		# 			for l in t.lavoro_set.all():
		# 				res &= (l.stato == self.stato)
		# 			if res:
		# 				self.team.intervento.stato = self.stato
		# 				self.team.intervento.save()
		# 	elif self.stato in (in_corso, assegnato):
		# 		self.team.intervento.stato = self.stato
		# 		self.team.intervento.save()
				
		# 	else:
		# 		self.stato = assegnato
		# 		self.save()
		res = super(Lavoro, self).save(*args, **kwargs)
		self.team.intervento.stato = self.team.intervento.calcola_stato()
		self.team.intervento.save()
		return res

	
	
	class Meta:
		verbose_name = _("Lavoro")
		verbose_name_plural = _("Lavoro")
		indexes = [ 
             models.Index(fields = ['stato', ]), 
             models.Index(fields = ['collaboratore', ]),
             models.Index(fields = ['team', ]),
             ]


class TempiLavoro(Base_a):
	
	"""
	Classe atta a registrare i tempi effettivi di lavoro.\n
	lavoro: fk a Lavoro per idrntifivsre il lavoro da svolgere\n
	inizio: data e dora di inizio della registrazione\n
	fine: data e ora di fine della registrszione\n
	note: annotazioni in merito al periodo di lavoro\n
	"""
	
	lavoro = models.ForeignKey(
		Lavoro,
		on_delete = models.PROTECT,
		verbose_name = _("Lavoro correlato"),
		)
	inizio = models.DateTimeField(
		_("Data e ora di Inizio"),
		default = datetime.datetime.now,
		)
	fine = models.DateTimeField(
		_("Data e ora di fine"),
		null = True,
		blank = True,
		)
	note = models.TextField(
		_("Annotazioni"),
		null = True,
		blank = True,
		)

	def __str__(self):
		text = "{lavor} - {data:%d/%m/%Y %H:%M}"
		return text.format(
			lavor = self.lavoro,
			data = self.inizio
			)
	
	class Meta:
		verbose_name = _("Tempo di lavoro")
		verbose_name_plural = _("Tempi di lavoro")


class Allegato(Base_a):
	
	"""
	Classe atta a contenere gli allegati delle segnalazioni.\n
	segnalazione: FK a Segnalazionr per indicare la segnalazione coinvolta\n
	file: campo per contenere il file allegato\n
	"""
	
	segnalazione = models.ForeignKey(
		Segnalazione,
		on_delete = models.CASCADE, 
		verbose_name = _("Segnalazione relativa"),
		)
	file = models.FileField(upload_to = "allegati/%Y/%m/")
	descrizione = models.TextField(
		default = "Allegato",
		max_length = 80,
		verbose_name = _("Descrizione")
		)

	def __str__(self):
		text = "{segn} - {nome}"
		return text.format(
			segn = self.segnalazione, 
			nome = self.file.name
			)
	
	class Meta:
		verbose_name = _("Allegato alla segnalazione")
		verbose_name_plural = _("Allegati alla segnalazione")


class Annotazione(Base_a):
	
	"""
	Classe atta a contenere le annotazioni ai lavori da parte di operai.\n
	testo: testo dell'annotazione\n
	lavoro: fk a Lavoro per indicare il lavoro coinvolto.\n
	"""
	
	lavoro = models.ForeignKey(
		Lavoro,
		on_delete = models.PROTECT,
		verbose_name = _("Lavoro correlato"),
		)
	testo = models.TextField(
	_("Annotazione"), 
	)

	def __str__(self):
		text = "{lav} - {data:%d/%m/%Y}"
		return text.format(
			lav = self.lavoro,
			data = self.data_creazione,
			)
	
	
	class Meta:
		verbose_name = _("Annotazione al lavoro")
		verbose_name_plural = _("Annotazioni al lavoro")

# classi through


class EventoSegnalazione(Base_a):
	
	"""
	Classe through per la M2M EventoSegnalazioneAnno\n
	"""
	
	evento = models.ForeignKey(
		Evento,
		on_delete = models.PROTECT,
		verbose_name = _("Evento"),
		)
	segnalazione = models.ForeignKey(
		Segnalazione,
		on_delete = models.PROTECT,
		verbose_name = _("Segnalazione"),
		)

	def __str__(self):
		text = "{evento} - {segnalazione}"
		return text.format(
			evento = self.evento,
			segnalazione = self.segnalazione
			)
	
	class Meta:
		verbose_name = _("Evento - Segnalazione")
		verbose_name_plural = _("Eventi - Segnalazioni")


class CollaboratoreMansione(Base_a, ValidDate_a):
	
	"""
	Classe through per la M2M di collaboratore su Mansione\n
	"""
	
	collaboratore = models.ForeignKey(
		Collaboratore,
		on_delete = models.PROTECT,
		verbose_name = _("Collaboratore"),
		)
	mansione = models.ForeignKey(
		Mansione,
		on_delete = models.PROTECT,
		verbose_name = _("Mansione"),
		)
	
	def __str__(self):
		text = "{coll} - {mans}"
		return text.format(
			coll = self.collaboratore,
			mans = self.mansione,
			)
	
	class Meta:
		verbose_name = _("Collaboratore - Mansione")
		verbose_name_plural = _("Collaboratori -Mansioni")
		
		
class CollaboratoreAssenza(Base_a, ValidDate_a):
	
	"""
	Classe through per la M2M di collaboratore su Assenza
	"""
	
	collaboratore = models.ForeignKey(
		Collaboratore,
		on_delete = models.PROTECT,
		verbose_name = _("Collaboratore"),
		)
	assenza = models.ForeignKey(
		Tipologia,
		on_delete = models.PROTECT,
		verbose_name = _("Tipo di assenza"),
		limit_choices_to = {'tipo' : ASSENZA},
		)
	
	def __str__(self):
		text = "{coll} - {ass}: {data_da:%d/%m/%Y} - {data_a:%d/%m/%Y}"
		return text.format(
			coll = self.collaboratore,
			ass = self.assenza,
			data_da = self.data_da,
			data_a = self.data_a,
			)
	
	class Meta:
		verbose_name = _("Periodo di assenza del Collaboratore")
		verbose_name_plural = _("Periodi di assenze del collaboratore")
		ordering = ['data_da']
		

class CollaboratoreReperibilita(Base_a, ValidDate_a):
	
	"""
	Classe through per la M2M di collaboratore su Reperibilità\n
	"""
	
	collaboratore = models.ForeignKey(
		Collaboratore,
		on_delete = models.PROTECT,
		verbose_name = _("Collaboratore"),
		)
	reperibilita = models.ForeignKey(
		Tipologia,
		on_delete = models.PROTECT,
		verbose_name = _("Tipo di reperibilità"),
		limit_choices_to = {'tipo' : REPERIBILITA},
		)	
	
	def __str__(self):
		text = "{coll} - {rep}: {data_da:%d/%m/%Y} - {data_a:%d/%m/%Y}"
		return text.format(
			coll = self.collaboratore,
			rep = self.reperibilita,
			data_da = self.data_da,
			data_a = self.data_a,
			)
	
	class Meta:
		verbose_name = _("Periodo di reperibilità del Collaboratore")
		verbose_name_plural = _("Periodi di reperibilità del collaboratore")
		ordering = ['data_da']