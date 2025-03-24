from django.contrib.gis.db import models
from colorfield.fields import ColorField
from django.utils import timezone

from django.utils.translation import gettext_lazy as _

from dipendenti.models import Dipendente

# funzioni generali 

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

# Costanti ed enumerazioni

STATO = "TO"
SEGNORIG = "SO"
SEGNTIPO = "ST"
FOTO = "FO"
ASSENZA = "AS"
REPERIBILITA = "RE"



	
"""
enumerazione per differenziare le varie tipologie esistenti 
STATO: vale per tutti gli oggetti ereditati da Status_a (aperto, chiuso , verificato...)
SEGNORIG: tipologie di origine delle segnalazioni
SEGNTIPO: tipologia di segnalazioni
FOTO: tipologie di foto (inizio, fine, corso di svolgimento)
ASSENZA: tipi di assenza(malattia, ferie, corso...)
REPERIBILITA: tipi di reperibilità (ordinaria, neve)
"""
tipologie = [
	(STATO, _("Stato")),
	(SEGNORIG, _("Origine Segnalazione")),
	(SEGNTIPO, _("Tipologia Segnalazione")),
	(FOTO, _("Tipologia di Foto")),
	(ASSENZA, _("Tipologia di assenza")),
	(REPERIBILITA, _("Tipologia di Reperibilità")),
	]

IT = "it"
DE = "de"
EN = "en"

lingue = [
	(IT, "Italiano"),
	(DE, "Deutsch"),
	(EN, "English"),
	]

# modelli astratti

class Base_a(models.Model):
	
	"""
	Classe astratta di base a tutti gli oggetti del progetto
	id: autofield di ID dell'oggetto
	data_creazione: data automatica di creazione
	data_modifica = data automatica di ultima modifica
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
	
class ItDe_a(models.Model):
	
	"""
	Classe con i campi di default per descrizione in italiano e tedesco:
	nome_breve: nome per le referenze interne e l'admin site
	nome_it e *_de = nomi brevi nelle due lingue per l'interfaccia web
	descrizione_it e *_de: descrizioni dettagliate nelle due lingue
	colore: esadecimale del colore associato per associazioni cromatiche
	"""
	
	nome_breve = models.CharField(
		_("Nome Breve per riferimenti interni"),
		max_length = 30,
		)
	nome_it = models.CharField(
		_("Nome italiano per l'interfaccia"),
		max_length = 40,
		)
	nome_de = models.CharField(
		_("Nome tedesco per l'interfaccia"),
		max_length = 40,
		)
	descrizione_it = models.TextField(
		_("Descrizione italiana per interfaccia"),
		)
	descrizione_de = models.TextField(
		_("Descrizione tedesca per interfaccia"),
		)
	colore = ColorField(
		)
	
	def __str__(self):
		text = "{nome}"
		return text.format(nome = self.nome_breve)
	
	class Meta:
		abstract = True
  
		
class Periodic_a(models.Model):
	
	"""
	classe per riportare i campi relativi agli elementi periodici
	periodico: boolean per indicare se l'elemento è periodico
	periodo: numero di giorni dopo la chiusura in cui l'evento si ripete
	cicli: nomero di cicli che si devono ripetere; se vuoto si ripete all'infinito
	duplicare: se vero, duplica gli elementi gerarchicamente sottostanti
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
	classe con i campi standard di descrizione degli elementi
	oggetto: descrizione sintetica
	descrizione: descrizione completa
	note: annotazioni aggiuntive
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
		text = "{testo}..."
		return text.format(testo = self.oggetto[:25])
	
	class Meta:
		abstract = True
		
class ValidDate_a(models.Model):
	
	"""
	classe con i campi di data che registrano una validità temporale
	data_da: data di inizio
	data_a: data di fine
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
	classe con il solo campo di stato, standardizzato per convenienza
	stato: FK a tipologia nel sottoinsieme di tipo STATO
	"""
	
	stato = models.ForeignKey(
		"Tipologia",
		on_delete = models.PROTECT,
		verbose_name = _("Stato dell'elemento"),
		limit_choices_to = {'tipo' : STATO},
		)

	class Meta:
		abstract = True	
		
class D3_a(models.Model):
	
	"""
	classe con i riferimenti al documentale; 
	estrapolato dal testo generale nel caso in cui cambiasse il riferimento.
	id_documento: campo document_id di D.3
	"""
	
	id_documento = models.CharField(
		_("ID D.3 del documento collegato"),
		null = True, blank = True,
		)

	class Meta:
		abstract = True  
		
class RABS_a(models.Model):
	
	"""
	classe per i riferimenti alle RABS;
	estrapolato dal testo generale nel caso in cui cambiasse il riferimento.
	id_RABS: compo document_id in D:3 della RABS
	"""
	
	id_RABS = models.CharField(
		_("ID D.3 della RABS collegata"),
		null = True, blank = True,
		)

	class Meta:
		abstract = True



# classi funzionali

class Mansione(Base_a, ItDe_a, ):
	
	"""
	Elenco delle varie mansioni; necessaria per lo smistamento dei lavori
	nessun campo specifico non ereditato.
	"""
	
	pass
	
	class Meta:
		verbose_name = _("Mansione")
		verbose_name_plural = _("Mansioni")


class Attivita(Base_a, ItDe_a, ):
	
	"""
	elenco delle attività dove incasellare i team di intervento.
	obbligo_foto: boolean per indicare se questa attività necessita di foto iniziale e finale
	chiusura_auto_lavoro: se false, il caposquadra deve verificare i lavori svolti
	tempo_stimato: valore indicativo in ore/uomo per svolgere il lavoro
	tempo_aumento: valore di giorni dopo il quale la priorità scala al livello successivo
	mansioni: m2m sulle mansioni che possono svolgere l'attività'
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
	
	class Meta:
		verbose_name = _("Attività")
		verbose_name_plural = _("Attività")


class Priorita(Base_a, ItDe_a):
	
	"""
	elenco di priorità standard, valorizzare con un numero intero
	valore: numero intero di indicizzazione delle priorità
	"""
	
	valore = models.IntegerField(
		_("Valore della Priorità"),
		)

	class Meta:
		verbose_name = _("Priorità")
		verbose_name_plural = _("Priorità")


class Anno(Base_a):
	
	"""
	classe che raccoglie gli anni di esercizio
	anno: stringa di 4 caratteri con l'anno'
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
	Classe che definisce una squadra di collaboratori.
	Nessun campo non ereditato.
	"""
	
	pass

	class Meta:
		verbose_name = _("Squadra")
		verbose_name_plural = _("Squadre")


class Tipologia (Base_a, ItDe_a):
	
	"""
	classe che racchiude tutte le tipologie, raggruppare con l'enum "tipologie"
	tipo: scleta del tipo di tipologia, legata all'enum "tipologie"
	abbreviazione: abbreviazione del tipo specifico, di tre lettere
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
	
	def __str__(self):
		text = "{nome} ({sigla}-{abbr})"
		return text.format(
			nome = self.nome_breve,
			sigla = self.tipo,
			abbr = self.abbreviazione,
			)
	
	class Meta:
		verbose_name = _("Tipologia")
		verbose_name_plural = _("Tipologie")
		unique_together = ["tipo", "abbreviazione"]


class Collaboratore(Base_a):
	
	"""
	classe che raggruppa i collaboratori del progetto.
	dipendente: fk a dipendenti.Dipendente, per collegare utente e diritti
	squadra: fk a Squadra, per assegnarlo ad una squadra operativa
	telefono: per segnare un cellularei di riferimento
	responsabile: boolean per indicare se un collaboratore sia o meno responsabile di struttura
	mansioni: m2m per le mansioni per cui è accreditato
	assenze: m2m per periodi di assenza
	reperibilita: m2 per periodi di reperibilità 
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

	def __str__(self):
		text = "{cognome} {nome}"
		return text.format(
			cognome = self.dipendente.cognome.upper(),
			nome = self.dipendente.nome,
			)
	
	class Meta:
		verbose_name = _("Collaboratore")
		verbose_name_plural = _("Collaboratori")


class CdC (Base_a,ItDe_a):
	
	"""
	Classe che raccoglie i centri di costo relativi alle strutture.
	note: annotazioni relative ai centri di costo.
	"""
	
	note = models.TextField(
		_("Annotazioni"),
		null = True, blank = True,
		)

	class Meta:
		verbose_name = _("Centro di costo")
		verbose_name_plural = _("Centri di costo")


class Struttura(Base_a, ItDe_a):
	
	"""
	tabella che contiene i dati di struttura, anche ointesa in senso lato, es: rete stradale.
	responsabile: FK a collaboratori filtrati per responsabile=True, che indica chi sia il responsabile di struttura
	cdc: fk a CdC per indicare il centro di costo relativo alla struttura
	indirizzo_it e _de: indirizzi in italiano e tedesco della struttura
	telefono: nimero di telefono di riferimento della struttura.
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
	indirizzo_it = models.CharField(
		_("Indirizzo in italiano"),
		max_length = 150,
		)
	indirizzo_de = models.CharField(
		_("Indirizzo in tedesco"),
		max_length = 150,
		)
	telefono = models.CharField(
		_("Numero di telefono"),
		max_length = 15,
		)
	
	class Meta:
		verbose_name = _("Struttura")
		verbose_name_plural = _("Strutture")


# classi operative

class Evento(Base_a, ItDe_a):
	
	"""
	Classe che agisce da contenitore e classificazione delle segnalazioni.
	nessun campo non ereditato.
	"""
	
	pass

	class Meta:
		verbose_name = _("Evento")
		verbose_name_plural = _("Eventi")


class Segnalazione(Base_a, Periodic_a, Description_a, Status_a, D3_a):
	
	"""
	Classe atta a contenere tutti i dati relativi ad una segnalazione di intervento.
	data_pianificazione: data di pianificazione della soluzione
	struttura: fk a strutture per identificare il luogo di intervento
	origine: fk a tipologia su SEGNORIG per indicare da dove provenga la segnalazione
	segnalatore: nome e cognome della persona segnalante
	email: indirizzo e-mail del segnalatore; se valorizzato, invia automaticamente una risposta quando chiusa.
	telefono: numero di telefono del segnalatore
	risposta: testo della risposta alla segnalazione da inviare un avolta conclusa.
	eventi: M2M per Evento, collega la segnalazione ad uno o più eventi (annui)
	tipo: fk a tipologia su SEGNTIPO per indicare la tipologia di segnalazione
	"""
	
	data_pianificazione = models.DateField(
		_("Data di pianificazione"),
#		null=True, blank=True,
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
		related_name = "segnalazione_origine",
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
		related_name = "segnalazioni",
		through = "EventoSegnalazione",
		)
	tipo = models.ForeignKey(
		Tipologia,
		on_delete = models.PROTECT,
		verbose_name = _("Tipo di segnalazione"),
		related_name = "segnalazione_tipo",
		limit_choices_to = {'tipo' : SEGNTIPO},
		)
	
	class Meta:
		verbose_name = _("Segnalazione")
		verbose_name_plural = _("Segnalazioni")


class Intervento(Base_a, Periodic_a, Description_a, Status_a, RABS_a):
	
	"""
	classe per raccogliere i dati degli interventi.
	segnalazione: fk a Segnalazione per collegare intervento ad eventuale segnalazione
	struttura: fk a struttura opzionale per identificare la struttura in caso di segnalazione assente
	priorita: fk a priorita per impostare la priorità iniziale dell'intervento
	preposto: fk a collaboratore, per indicare chi sia l'operaio preposto all'intervento
	precedente: pk a Intervento per indicare l'intervento che lo precede logicamwnte (intervento di origine di questo)
	data_visibilita: l'intervento sarà visibile in interfaccia a partie dalla data indicata
	data_urgente: l'intervento avrà la massima urgenza a decorrere da questa data
	data_esecuzione: l'intervento potrà essere eseguibile a partire dalla data indicata
	provvisorio: l'intervento è provvisorio, ovvero da completare
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
		default = timezone.now,
		help_text = _("Data a partire dalla quale l'intervento diventa visibile."),
		)
	data_urgente = models.DateField(
		_("Data di urgenza"),
		help_text = _("Data a partire dalla quale l'intervento diventa urgente."),
		null = True, blank = True,
		)
	data_esecuzione = models.DateField(
		_("Data di esecuzione"),
		default = timezone.now,
		help_text = _("Data a partire dalla quale l'intervento può venire risolto."),
		) 
	provvisorio = models.BooleanField(
		_("Intervento provvisorio"),
		default = False, 
		help_text = _("Intervento incompleto inserito da sistema"), 
		)

	class Meta:
		verbose_name = _("Intervento")
		verbose_name_plural = _("Interventi")

class Team(Base_a):
	
	"""
	Classe atta a raccoglere i dati relativi ad un team di intervento di risoluzione di un intervento.
	intervento: FK ad Intervento per collegarlo all'intervento relativo
	attivita: tipologia di attività da svolgere dal team
	tempo_stimato: tempo stimato di soluzione dell'intervento per il team, in ore uomo. 
		Il valore sovrascrive quello dell'attività, se impostato.
	tempo_aumento: tempo dopo il quale la priorità dell'intervento sale di urgenza.
		Il valore sovrascrive quello dell'attività, se impostato.
	"""
	
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
		help_text = _("Il valore si intende indicato in ore/uomo"),
		)
	tempo_aumento = models.IntegerField(
		_("Tempo di aumento della priorità"), 
		help_text = _("Tempo dopo il quale la priorità aumenta di grado. Il valore si intende indicato in giornate"),
		)

	def __str__(self):
		text = "{interv} - {att}"
		return text.format(
			interv = self.intervento, 
			att = self.attivita,
			)
	
	class Meta:
		verbose_name = _("Team di intervento")
		verbose_name_plural = _("Teams di intervento")

class Foto(Base_a):
	
	"""
	Classe atta a contenere le foto effettuate dagl operai in sede di lavoro.
	tipoogia: fk a Tipologia su FOTO, indica se la foto È iniziale, finale o in corso d'opera
	intervento: fk a Intervento per indicare a quale intervento sia collegata.
	collaboratore: fk a Collaboratore che iundica chi sia l'autore della foto
	foto: imagefield con l'immagine relativa
	posizione: punto geografico che geolocalizza la foto
	note: annotazioni in merito alla foto.
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
	posizione = models.PointField()
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
	Classe adita a contenere i dati relativi ad un lavoro assegnato
	collaboratore: fk a Collaboratore, per indicare a quale operaio venga assegnato il lavoro
	team: fk a Team per capire quale team d'intervento venga assegnato
	durata_prevista: ore-uomo di lavoro previsto
	caposquadra: id del caposwquadra che verifica il lavoro (se richiesto)
	accessorio: boolean che se vero, indica che il lavoro È accessorio all'intervento
	urgenza: lavoro svolto in carattere di urgenza
	mod_priorita: modifica manuale della priorità del lavoro.
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
	
	class Meta:
		verbose_name = _("Lavoro")
		verbose_name_plural = _("Lavoro")


class TempiLavoro(Base_a):
	
	"""
	Classe atta a registrare i tempi effettivi di lavoro.
	lavoro: fk a Lavoro per idrntifivsre il lavoro da svolgere
	inizio: data e dora di inizio della registrazione
	fine: data e ora di fine della registrszione
	note: annotazioni in merito al periodo di lavoro
	"""
	
	lavoro = models.ForeignKey(
		Lavoro,
		on_delete = models.PROTECT,
		verbose_name = _("Lavoro correlato"),
		)
	inizio = models.DateTimeField(
		_("Data e ora di Inizio"),
		default = timezone.now,
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
	Classe atta a contenere gli allegati delle segnalazioni.
	segnalazione: FK a Segnalazionr per indicare la segnalazione coinvolta
	file: campo per contenere il file allegato
	"""
	
	segnalazione = models.ForeignKey(
		Segnalazione,
		on_delete = models.CASCADE, 
		verbose_name = _("Segnalazione relativa"),
		)
	file = models.FileField(upload_to = "allegati/%Y/%m/")

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
	Classe atta a contenere le annotazioni ai lavori da parte di operai.
	testo: testo dell'annotazione
	lavoro: fk a Lavoro per indicare il lavoro coinvolto.
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
	Classe through per la M2M EventoSegnalazioneAnno
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
	anno = models.ForeignKey(
		Anno,
		on_delete = models.PROTECT,
		verbose_name = _("Anno di riferimento"),
		)

	def __str__(self):
		text = "{evento} {anno} - {segnalazione}"
		return text.format(
			evento = self.evento,
			anno = self.anno,
			segnalazione = self.segnalazione
			)
	
	class Meta:
		verbose_name = _("Evento - Anno-segnalazione")
		verbose_name_plural = _("Eventi - Anni - Segnalazioni")

class CollaboratoreMansione(Base_a, ValidDate_a):
	
	"""
	Classe through per la M2M di collaboratore su Mansione
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
		

class CollaboratoreReperibilita(Base_a, ValidDate_a):
	
	"""
	Classe through per la M2M di collaboratore su Reperibilità
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