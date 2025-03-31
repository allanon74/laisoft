from django.db import models
from django import forms
from django.db.models import Q 
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.html import format_html, strip_tags

from django.utils.translation import gettext_lazy as _

import datetime
import os
import re

NA = "na"

def CompilaMailDip(testo, dip):

	serv = dip.dipendente_servizio_set.all().order_by('-data_da')[0]
	ruo = dip.dipendente_ruolo_set.all().order_by('-data_da')[0]
	qual = dip.dipendente_qualifica_set.all().order_by('-data_da')[0]
	td = "a tempo indeterminato."
	if qual.determinato:
		td= "a tempo determinato."
	return testo.format(
			nome = dip.nome,
			cognome=dip.cognome,
			indirizzo = dip.indirizzo,
			citta = dip.citta,
			cf = dip.codicefiscale,
			patentino = dip.patentino,
			datanascita = dip.data_nascita,			
			luogonascita = dip.luogo_nascita,
			matricola = dip.matricola,
			datainizio = ruo.data_da,
			datafine = ruo.data_a,
			profilo = qual.qualifica, 
			rapporto = qual.rapportolavoro.descrizione,
			tpd= td,
			userid=dip.userid,
			email=dip.email,
			tel=dip.telefono,
			cel=dip.cellulare,
			serv= serv.servizio.nome_it_m,
			uff=serv.servizio.ufficio_al().nome_it_m,
		)

class SeparatedValuesField(models.TextField):
  #  __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
        super(SeparatedValuesField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value: return
        if isinstance(value, list):
            return value
        return value.split(self.token)

    def get_db_prep_value(self, value):
        if not value: return
        assert(isinstance(value, list) or isinstance(value, tuple))
        return self.token.join([unicode(s) for s in value])

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


TESTO_AIUTO = "{nome}: nome del dipendente <br />" +os.linesep
TESTO_AIUTO += "{cognome}: cognome del dipendente<br />" +os.linesep
TESTO_AIUTO += "{indirizzo}: indirizzo del dipendente<br />" +os.linesep
TESTO_AIUTO += "{citta}: cap e dittà del dipendente<br />" +os.linesep
TESTO_AIUTO += "{cf}: codice fiscale del dipendente<br />" +os.linesep
TESTO_AIUTO += "{patentino}: patentino del dipendente<br />" +os.linesep
TESTO_AIUTO += "{datanascita}: data di nascita del dipendente<br />" +os.linesep
TESTO_AIUTO += "{luogonascita}: luogo di nascita del dipendente<br />" +os.linesep
TESTO_AIUTO += "{matricola}: matricole del dipendente<br />" +os.linesep
TESTO_AIUTO += "{datainizio}: data di inquadramento del dipendente<br />" +os.linesep
TESTO_AIUTO += "{datafine}: data di cessazione del dipendente<br />" +os.linesep
TESTO_AIUTO += "{profilo}: profilo professionale del dipendente<br />" +os.linesep
TESTO_AIUTO += "{rapporto}: raporto di lavoro del dipendente<br />" +os.linesep
TESTO_AIUTO += "{tpd}: tempo determinato - indeterminato<br />" +os.linesep
TESTO_AIUTO += "{userid}: nome utente del dipendente<br />" +os.linesep
TESTO_AIUTO += "{email}: e-mail del dipendente<br />" +os.linesep
TESTO_AIUTO += "{tel}: numero di telefono del dipedente<br />" +os.linesep
TESTO_AIUTO += "{cel}: numero di cellulare del dipedente<br />" +os.linesep
TESTO_AIUTO += "{serv}: servizio a cui è associato il dipendente<br />" +os.linesep
TESTO_AIUTO += "{uff}: ufficio a cui è assegnato il dipendente"

def mail_completo(destinatario, mittente, documento, url, titolo, testo):
# 	txt = 'Buon giorno. Ti è stata assegnata una nuova pratica da espletare.\r\n\r\n'
# 	txt += 'Il documento {}, relativo alla pratica, lo trovi qui: {}\r\n\r\n'
# 	txt += 'Il riepilogo delle pratiche lo trovi al link http://leifersdjango.leifers.gvcc.net/pratiche/lista/\r\n\r\n'
# 	txt += 'Cordiali saluti.\r\n\r\n'
# 	txt += 'Il dirigente \r\n\r\n'
# 	txt += 'Arch. Alessandra Montel'

  
#	Sendmail disabilitato per errori di login 

	res = send_mail(subject= titolo, 
				 message= format_html(testo, documento, url), 
				 from_email= mittente, 
				 recipient_list= (destinatario, ), 
				 fail_silently= False
	)
	
#	#res = "NA"	


	return res


# Models DIPENDENTI
# Create your models here.

# CHOICES

class Patentini(models.TextChoices):
	A2 = "A2", _('Patentino A2')
	B1 = "B1", _('Patentino B1')
	B2 = "B2", _('Patentino B2')
	C1 = "C1", _('Patentino C1')

SESSO_CHOICES = [
	('M', 'Maschio'),
	('F', 'Femmina'),
	('*', 'Non Espresso'),
]


TRUE_FALSE_CHOICES = [
	(True, "Sì"), (False, "No")
]

# static file path
def image_path():
	return os.path.join(settings.LOCAL_FILE_DIR, 'logo')

# Classi Astratte

class Base_abstract(models.Model):
	id = models.AutoField("Codice Identificativo", 
					   primary_key=True, 
					   help_text="Id unico - chiave primaria",
					   )
	class Meta:
		abstract = True

class Date_through_abstract(Base_abstract):
	data_da = models.DateField(
		"Data di inizio", 
		default = timezone.now, 
		help_text = "Data di inizio del periodo",
		)
	#data_da = models.DateField("Data di inizio", default= ('01/01/2022'), )
	data_a = models.DateField(
		"Data di fine", 
		null=True, 
		blank = True, 
		help_text = "Data di fine del periodo",
		)
	#note = models.TextField("Annotazioni", null=True, blank=True, )
	
	class Meta:
		ordering = ['data_da', ]
		abstract = True

class Multi_abstract(Base_abstract):
	
	"""
	
	CLasse astratta con nomi tedesco-italiano e loro verisoni plurali.
	Creata per compilazione dei moduli di stampa bilingue.
	
	"""
	
	nome = models.CharField(
		"Nome Breve", 
		max_length= 20, 
		help_text = "Nome breve per il riferimento interno nel programma",
		)
	nome_it_m = models.CharField(
		"Nome italiano maschile", 
		max_length= 100, 
		help_text = "Nome esteso in italiano, per soggetti maschili.",
		)
	nome_it_f = models.CharField(
		"Nome italiano femminile", 
		max_length= 100, 
		null = True, 
		blank = True, 
		help_text = "Nome esteso in italiano, per soggetti femminili.",
		)
	nome_dt_m = models.CharField(
		"Nome tedesco maschile", 
		max_length= 100, 
		null = True, 
		blank = True, 
		help_text = "Nome esteso in tedesco, per soggetti maschili.",		
		)
	nome_dt_f = models.CharField(
		"Nome tedesco femminile", 
		max_length= 100, 
		null=True, 
		blank = True, 
		help_text = "Nome esteso in tedesco, per soggetti femminili..",		
		)
	
	def __str__(self):
		return self.nome
	class Meta:
		abstract = True


class Dipendente_through_abstract(Date_through_abstract):
	dipendente = models.ForeignKey(
		"Dipendente", 
		on_delete=models.CASCADE, 
		help_text = "Dipendnete collegato",
		)
	
	class Meta:
		abstract = True

class Html_abstract(Base_abstract):
	nome = models.CharField("Nome", max_length=30, unique=True, )
	titolo = models.CharField("Titolo", max_length=50, default="Titolo", )
	testo = models.TextField("Testo", default = "Testo",)
	ordine = models.IntegerField("Ordine", default=1,)
	pubblicato = models.BooleanField("In pubblicazione", default=False)


	class Meta:
		verbose_name = "html"
		verbose_name_plural = "html"
		abstract=True

	def __str__(self):
		return self.nome

	@classmethod
	def cerca(self, nome):
		tst = self.objects.filter(nome=NA)
		na = None
		if tst.count()==0:
			na = self(nome=NA, testo = "Pagina in elaborazione", titolo = "Pagina in elaborazione", pubblicato=True)
		else:
			na = tst[0]
			na.pubblicato = True
		na.save()

		scr = self.objects.filter(nome=nome)
		res = None
		if scr.count() == 0:
			res = self(nome=nome, testo = "Generato automaticamente", titolo = "Testo generato automaticamente")
			res.save()
		else:
			res = scr[0]
		if res.pubblicato==False:
			res = na
		return res
	
	@classmethod
	def online(self):
		return self.objects.filter(pubblicato=True).exclude(nome=NA)

# Classi Reali

class Immagine(Base_abstract):
	nome = models.CharField("Nome dell'immagine", max_length=30, unique=True, )
	descrizione=models.TextField("Descrizione alternativa", null=True, blank=True, )
	img=models.ImageField("Immagine", upload_to="immagini/", null=True, blank=True, )
	risoluzione=models.CharField("Risoluzione dell'immagine", max_length=15, default="320x200",)

	def __str__(self):
		return self.nome
	
	@classmethod
	def cerca(self, nome):
		scr = self.objects.filter(nome=nome)
		res = None
		if scr.count() == 0:
			res = self(nome=nome, descrizione = "Generato automaticamente", )
			res.save()
		else:
			res = scr[0]
		return res

	class Meta:
		verbose_name = "Wiki - Immagine"
		verbose_name_plural = "Wiki - Immagini"

class Pagina(Html_abstract):

	class Meta:
		verbose_name = "Wiki - Pagina"
		verbose_name_plural = "Wiki - Pagine"
		ordering = ["ordine", ]	

	def __str__(self):
		return self.nome

	def sezioni(self):
		return self.sezione_set.all().filter(pubblicato=True)

class Sezione(Html_abstract):
	pagina = models.ForeignKey(Pagina, on_delete=models.PROTECT, verbose_name="Pagina relativa", null=True, blank=True, )

	class Meta:
		verbose_name = "Wiki - Sezione"
		verbose_name_plural = "Wiki - Sezioni"
		ordering = ["ordine", ]

	def voci(self):
		return self.voce_set.all().filter(pubblicato=True)

class Voce(Html_abstract):
	sezione = models.ForeignKey(Sezione, on_delete=models.PROTECT, verbose_name="Sezione relativa", null=True, blank=True, )

	class Meta:
		verbose_name = "Wiki - Voce"
		verbose_name_plural = "Wiki - Voci"
		ordering = ["ordine", ]


class Capoverso(Base_abstract):
	testo = models.TextField("Testo", default = "Testo",)
	ordine = models.IntegerField("Ordine del capoverso", default=1,)
	voce = models.ForeignKey(
		Voce,
		verbose_name = "Voce relativa",
		on_delete=models.PROTECT
	)
	immagine = models.ForeignKey(
		Immagine,
		verbose_name = "Immagine",
		on_delete = models.PROTECT,
		null = True, blank=True,
	)
	allegato = models.ForeignKey(
		"Allegato",
		verbose_name = "Allegato",
		on_delete = models.PROTECT,
		null = True, blank=True,
	)

	class Meta:
		verbose_name = "Wiki - Capoverso"
		verbose_name_plural = "Wiki - Capoversi"
		ordering = ["ordine", ]
		#order_with_respect_to = "pagina"


class Allegato(Base_abstract):
	nome = models.CharField("Nome dell'allegato", max_length=30, unique=True, )
	descrizione=models.TextField("Descrizione link", null=True, blank=True, )
	file=models.FileField("File", upload_to="allegati/%Y/", null=True, blank=True, )

	class Meta:
		verbose_name = "Wiki - Allegato"
		verbose_name_plural = "Wiki - Allegati"

	def __str__(self):
		return self.nome
	
	@classmethod
	def cerca(self, nome):
		scr = self.objects.filter(nome=nome)
		res = None
		if scr.count() == 0:
			res = self(nome=nome, descrizione = "Generato automaticamente", )
			res.save()
		else:
			res = scr[0]
		return res	


class Mail(Base_abstract):
	helpt= "Separare i destinatari con un punto e virgola (;). <br /> Non terminare la linea con un punto e virgola."
	
	nome = models.CharField('Nome della e-mail', max_length=30, default="Testo di prova.", unique=True)
	mittente = models.EmailField('Mittente', default="mail@comune.laives.bz.it")
	oggetto = models.CharField('Oggetto', max_length=60, default="Comunicazione", )
	testo = models.TextField('Testo della E-mail', help_text = TESTO_AIUTO,)
	to = models.CharField("Elenco destinatari", max_length=512, help_text= helpt, default="mail@comune.laives.bz.it" )
	cc= models.CharField("Destinatari in copia conoscenza", max_length=512, help_text=helpt, null=True, blank=True,)
	del_cessazione = models.BooleanField("Inviare atto di cessazione?", default=False)


	def __str__(self):
		return self.nome

	class Meta:
		verbose_name = "Testo E-mail"
		verbose_name_plural = "Testi E-mail"

	def save(self, *args, **kwargs):
		if self.to[-1] == ";":
			self.to = self.to[:-1]
		if self.cc:
			if self.cc[-1] == ";":
				self.cc = self.cc[:-1]
		return super(Mail, self).save(*args, **kwargs)

class Logo(Base_abstract):
	"""
	Classe di memorizzazione dell'immagine del logo.
	

	"""
	immagine = models.ImageField(
		upload_to='logo/', 
		verbose_name="File immagine",
		help_text = "file di immagine del logo",
		)
	descrizione = models.CharField(
		"Descrizione del logo", 
		max_length=50, 
		unique=True, 
		help_text = "testo descrittivo del logo",
		)
	
	def __str__(self):
		return self.descrizione
	
	class Meta:
		verbose_name = 'Logo'
		verbose_name_plural = 'Logo'

class Ruolo(Multi_abstract):
	
	"""
	Classe Ruolo: definizione del ruolo nell'amministrazione.
	il flag "dirigente" abililita l'utente a comparire nelle DDL dei dirigenti
	idem per quello dei responsabili, sindaco e segretario
	il flag "ammistema" è per indicare chi sia amministratore di sistema
	ogni singolo ruolo è formato da uno o più "diritti"
	
	"""
	
	nome = models.CharField(
		"Nome Ruolo", 
		max_length= 20, 
		help_text = "Nome del ruolo per i riferimenti interni al programma",
		)
	dirigente = models.BooleanField(
		"Ruolo dirigenziale", 
		default=False, 
		help_text = "Indica che il ruolo ricopre la carica direttiva e dirigenziale, a capo di un ufficio. L'utente compare nei dropdown relativi.",
		)
	#coordinatore = models.BooleanField("Ruolo di coordinamento", default=False, )
	responsabile = models.BooleanField(
		"Ruolo di responsabile o coordinatore", 
		default=False, 
		help_text = "Indica che il ruolo ricopre la carica di responsabile di servizio o coordinatore di unità organizzativa. L'utente compare nei dropdown relativi.",
		)
	segretario = models.BooleanField(
		"Ruolo segretario generale", 
		default=False, 
		help_text = "Indica che il ruolo ricopre la carica di segretario o vice-segretario generale.",
		)
	ammsistema = models.BooleanField(
		"Ruolo amministratore di sistema", 
		default=False, 
		help_text = "Indica che il ruolo ha pieno accesso alla banca dati, in qualità di amministratore di sistema.", 
		)
	sindaco = models.BooleanField(
		"Ruolo da sindaco", 
		default=False, 
		help_text = "Il ruolo che compete al sindaco o vice-sindaco.",
		)
	
	class Meta:
		verbose_name = "Ruolo"
		verbose_name_plural = "Ruoli"
		ordering = ['nome', ]

class Livello(Base_abstract):
	
	"""
	Livello della qualifica funzionale
	"""
	
	livello = models.CharField(
		"Livello", 
		max_length= 10, 
		help_text = "Nome del livello, in numeri romani.",	
		)
	indice = models.IntegerField(
		"Indice", 
		help_text = "posizione del livello, per elenchi ordinali.",
		)
	coefficiente = models.IntegerField(
		"Coefficiente premio produzione", 
		help_text = "Valore contrattuale da applicare ala quota premio produzione, relativo al livello.",
		)
	
	def __str__(self):
		return self.livello
	
	class Meta:
		verbose_name = "Livello"
		verbose_name_plural = "Livelli"
		ordering = ['indice', ]

class Qualifica(Multi_abstract):
	
	"""
	Elenco delle varie qualifiche funzionali prese dal T.U. del 02.07.2015 nel testo vigente.
	"""
	
	nome = models.CharField("Nome Qualifica", 
						 max_length= 20, 
						 help_text = "Nome breve della qualifica funzionale, per i riferimenti interni.",
						 )
	livello = models.ForeignKey('Livello', 
							 on_delete=models.CASCADE, 
							 verbose_name="Livello", 
							 help_text = "FK qualifica funzionale - livello relativo, come da T.U. del 02.07.2015.",
							 )
	
	def __str__ (self):
		txt = "{nome} ({liv})"
		return txt.format(nome=self.nome, liv = self.livello)
		
	class Meta:
		verbose_name = "Qualifica"
		verbose_name_plural = "Qualifiche"
		ordering = ['livello__indice','nome',  ]
		
class RapportoLavoro(Base_abstract):
	
	"""
	
	Definizione del rapporto di lavoro con esplicitazione sia del teorico di minuti lavorati per settimana 
	che della percentuale effettiva, salvata in "coefficiente"
	
	"""
	
	descrizione = models.CharField(
		"Descrizione", 
		max_length = 30, 
		help_text = "Testo descrittivo ad uso interno per il rapporto di lavoro.",
		)
	n_minuti = models.IntegerField(
		"Totale teorico contrattuale settimanale di minuti lavorati", 
		help_text = "Si calcola sulla base di 2280 minuti, che sono equivalenti a 38 ore settimanali (full time).",
		)
	coefficiente = models.DecimalField(
		"Coefficiente rapporto di lavoro", 
		max_digits=6, 
		decimal_places = 5,
		help_text = "Coefficiente REALE di rapporto tra minuti settimanali contrattuali e minuti teorici (2280).",
		)

	def __str__(self):
		return self.descrizione
		
	class Meta:
		verbose_name = "Rapporto di lavoro"
		verbose_name_plural = "Rapporti di lavoro"
		ordering = ['-coefficiente', ]

class Ufficio(Multi_abstract):
	
	"""
	
	definizione del singolo ufficio dell'ente
	M2M che riporta il dirigente è attraverso Ufficio_Dirigente
	
	"""
	
	nome = models.CharField(
		"Nome Ufficio", 
		max_length= 20, 
		help_text = "Testo descrittivo ad uso interno dell'ufficio.",
		)
	dirigente = models.ManyToManyField(
		"Dipendente",
		related_name = "dirigente",
		through='Ufficio_Dirigente',
		through_fields = ('ufficio', 'dirigente'),
		help_text = "Many to Many di associazione tra ufficio e relativo dirigente. La DDL relativa si compila con i dipendenti i cui ruoli hanno il diritto 'responsabile'",
	)

	formula_responsabile_it = models.CharField("Denominazione del dirigente in italiano", max_length=100, default="Direttore dell'Ufficio")
	formula_responsabile_dt = models.CharField("Denominazione del dirigente in tedesco", max_length=100, default="Leiter des Amtes")

	def dirigente_al(self, data = datetime.datetime.now()):
		
		"""
		
		Metodo che restituisce un oggetto :model:`dipendenti.Dipendente` che è in ruolo a dirigente
		dell'ufficio alla data "data". Se omessa, il default è la data odierna.
		Se alla data indicata non risulta alcun dirigente, la funzione restituisce None
		
		"""
		
		qdip = Ufficio_Dirigente.objects.filter(ufficio__exact= self.id).exclude(Q(data_da__gte=data)).exclude(Q(data_a__lt=data)).order_by('-data_da')
		if qdip.count() == 0:
			rl = None
		else:
			rl = qdip[0].dirigente
		return rl
	
	class Meta:
		verbose_name = "Ufficio"
		verbose_name_plural = "Uffici"
		ordering = ['nome', ]

class Servizio(Multi_abstract):
	
	"""
	
	Definizione del singolo "servizio" sia formalmente individuato che informalmente
	utilizzato come raggruppamento di dipendenti nell'ente
	M2M per Ufficio di appartenenza è attraverso :model:`dipendenti.Servizio_Ufficio`
	M2M per responsabile incaricato è attraverso :model:`dipendenti.Servizio_Responsabile`
	"Esente IRAP" è un dato utile per l'ufficio personale ai fini retributivi
	(da attivare per servizi scolastici)
		
	"""
	
	nome = models.CharField("Nome Servizio", max_length= 20, )
	ufficio = models.ManyToManyField(
		Ufficio,
		through='Servizio_Ufficio',
	)
	esente_irap = models.BooleanField("Servizio esente IRAP", default=False, )

	responsabile = models.ManyToManyField(
		"Dipendente",
		related_name = "responsabile",
		through='Servizio_Responsabile',
		through_fields = ('servizio', 'responsabile'),
	)
	
	formula_responsabile_it = models.CharField("Denominazione del responsabile in italiano", max_length=100, default="Responsabile del servizio")
	formula_responsabile_dt = models.CharField("Denominazione del responsabile in tedesco", max_length=100, default="Verantwortlicher des Dienstes")
	email = models.EmailField("E-mail", max_length= 100, null=True, blank=True)
	telefono = models.CharField("Telefono", max_length= 40, null=True, blank=True)
	cdc = models.CharField("Centro di Costo", max_length= 40, null=True, blank=True)

	def responsabile_al(self, data = datetime.datetime.now()):
		
		"""
		
		Metodo che restituisce un oggetto :model:`dipendenti.Dipendente` che è in ruolo a responsabile
		del servizio alla data "data". Se omessa, il default è la data odierna.
		Se alla data indicata non risulta alcun responsabile, la funzione restituisce None
		
		"""
		
		qdip = Servizio_Responsabile.objects.filter(servizio__exact= self.id).exclude(Q(data_da__gt=data)).exclude(Q(data_a__lt=data)).order_by('-data_da')
		if qdip.count() == 0:
			rl = None
		else:
			rl = qdip[0].responsabile
		return rl
		
	def ufficio_al(self, data = datetime.datetime.now()):
		
		"""
		
		Metodo che restituisce un oggetto :model:`dipendenti.Ufficio` a cui il servizio è collegato
		alla data "data". Se omessa, il default è la data odierna.
		Se alla data indicata non risulta alcun Ufficio, la funzione restituisce None
		
		"""
		
		qdip = Servizio_Ufficio.objects.filter(servizio__exact= self.id).exclude(Q(data_da__gt=data)).exclude(Q(data_a__lt=data)).order_by('-data_da')
		if qdip.count() == 0:
			rl = None
		else:
			rl = qdip[0].ufficio
		return rl
	
	def dirigente_al(self, data = datetime.datetime.now()):
		
		"""
		
		Metodo che restituisce un oggetto :model:`dipendenti.Dipendente` che è in ruolo a dirigente
		dell'ufficio cui appartiene il servizio alla data "data". 
		Se omessa, il default è la data odierna.
		Se alla data indicata non risulta alcun dirigente, la funzione restituisce None
		Richiama il metodo omonimo della classe :model:`dipendenti.Ufficio` 
		
		"""
		if self.ufficio_al(data) is None:
			return None
		else:
			return self.ufficio_al(data).dirigente_al(data)

	class Meta:
		verbose_name = "Servizio o gruppo di attività omogenee"
		verbose_name_plural = "Servizi e gruppi di attività omogenee"
		ordering = ['nome', ]


class Dipendente(models.Model):
	
	"""
	
	Classe principale della gestione dei dipendenti.
	Tramite userid si crea un soft one-to-one FK con users.
	
	
	"""
	NOTA_TIT_PRINC = "Se valorizzato, sovrascrive qualunque altro titolo previsto."

	id = models.AutoField("Codice Identificativo", primary_key=True, )
	matricola = models.CharField("Matricola", max_length= 6, null=True, blank=True, )
	badge_p = models.CharField("Numero Badge apertura porte", max_length=8, null=True, blank=True, )
	nome = models.CharField("Nome", max_length= 40, )
	cognome = models.CharField("Cognome", max_length= 40, )
	indirizzo = models.CharField("Via e numero civico", max_length=120, null=True, blank=True, )
	citta = models.CharField("CAP e città di residenza", max_length=120, null=True, blank=True, )
	data_nascita = models.DateField("Data di nascita", null=True, blank=True, )
	luogo_nascita = models.CharField("Luogo di nascita", max_length=100, null=True, blank=True,  )
	codicefiscale = models.CharField("Codice Fiscale", max_length=16, null=True, blank=True, )
	sesso = models.CharField("Sesso", max_length=1, null=True, blank=True, choices=SESSO_CHOICES, )
	patentino = models.CharField("Patentino di bilinguismo", max_length=2, null=True, blank=True, choices=Patentini.choices)
	userid = models.CharField("Nome Utente", max_length= 16, null=True, blank=True, )
	email = models.EmailField("E-mail", max_length= 100, null=True, blank=True)
	telefono = models.CharField("Telefono", max_length= 40, null=True, blank=True)
	cellulare = models.CharField("Cellulare", max_length= 40, null=True, blank=True)
	catprotetta = models.BooleanField("Categoria Protetta", default=False, )
	note = models.TextField("Note aggiuntive", null=True, blank=True)
	attivo = models.BooleanField('Utente attivo', default=True,)
	titprinc_it = models.CharField("Titolo principale in italiano", max_length= 140, null=True, blank=True, help_text=NOTA_TIT_PRINC, )
	titprinc_dt = models.CharField("Titolo principale in tedesco", max_length= 140, null=True, blank=True, help_text=NOTA_TIT_PRINC, )
	ruolo = models.ManyToManyField(
		Ruolo,
		through='Dipendente_Ruolo',
		through_fields = ('dipendente', 'ruolo'),
	)
	qualifica = models.ManyToManyField(
		Qualifica,
		through='Dipendente_Qualifica',
		through_fields = ('dipendente', 'qualifica'),
	)
	servizio = models.ManyToManyField(
		Servizio,
		through='Dipendente_Servizio',
		through_fields = ('dipendente', 'servizio'),
	)
	det_cessazione = models.FileField("Determina / delibera di cessazione", upload_to="atti_dip/%Y/", null=True, blank=True,)


# 	user = models.OneToOneField(
# 		settings.AUTH_USER_MODEL, 
# 		null=True, 
# 		blank=True, 
# 		on_delete=models.CASCADE, 
# 	)
	

	def __str__(self):
		return '%s %s' % (self.cognome.upper(), self.nome)
	
	@property
	def user(self):
		res = User.objects.filter(username = self.userid)
		if res.count() == 0:
			return None
		else:
			return res[0]
		
	def get_dipendente(user):
		res = Dipendente.objects.filter(userid = user.username)
		if res.count() == 0:
			return None
		else:
			return res[0]
	
	def ruolo_al(self, data = datetime.datetime.now()):
# 		rdip = Dipendente_Ruolo.objects.filter(dipendente__exact= self.id).exclude(Q(data_da__gt=data)).exclude(Q(data_a__lt=data)).order_by('-data_da')[0]
# 		if rdip is None:
# 			rl = None
# 		else:
# 			rl = rdip.ruolo
		qdip = Dipendente_Ruolo.objects.filter(dipendente__exact= self.id).exclude(Q(data_da__gt=data)).exclude(Q(data_a__lt=data)).order_by('-data_da')
		if qdip.count() == 0:
			rl = None
		else:
			rl = qdip[0].ruolo
		return rl
		
	def qualifica_al(self, data = datetime.datetime.now()):
		qdip = Dipendente_Qualifica.objects.filter(dipendente__exact= self.id).exclude(Q(data_da__gt=data)).exclude(Q(data_a__lt=data)).order_by('-data_da')
		if qdip.count() == 0:
			rl = None
		else:
			rl = qdip[0].qualifica
		return rl
	
	def servizio_al(self, data = datetime.datetime.now()):
		qdip = Dipendente_Servizio.objects.filter(dipendente__exact= self.id).exclude(Q(data_da__gt=data)).exclude(Q(data_a__lt=data)).order_by('-data_da')
		if qdip.count() == 0:
			rl = None
		else:
			rl = qdip[0].servizio
		return rl
	
	def responsabile_al(self, data = datetime.datetime.now()):
		if self.servizio_al(data) is None:
			return None
		else:
			return self.servizio_al(data).responsabile_al(data)

	def ufficio_al(self, data = datetime.datetime.now()):
		if self.servizio_al(data) is None:
			return None
		else:
			return self.servizio_al(data).ufficio_al(data)
		
	def dirigente_al(self, data = datetime.datetime.now()):
		if self.servizio_al(data) is None:
			return None
		else:
			return self.servizio_al(data).dirigente_al(data)
	
	def num_servizi(self):
		return self.servizio.count()
	
	def dipendente_dal(self):
		prima_qual = Dipendente_Qualifica.objects.filter(dipendente__exact= self.id).order_by('data_da')[0]
		return prima_qual.data_da
	
	def dettaglio(self):
		txt = "{cognome} {nome}\r\n"
		txt += "{ufficio} - {servizio}\r\n"
		txt += "tel: {telefono}\r\n"
		txt += "e-mail: {email}"
		
		uff = ""
		serv = ""
		if self.ufficio_al() is None:
			uff = "non in servizio"
		else:
			uff = self.ufficio_al().nome_it_m
			
		if self.servizio_al() is None:
			serv = ""
		else:
			serv = self.servizio_al().nome_it_m

		return txt.format(cognome=self.cognome, nome=self.nome, ufficio=uff, servizio=serv, telefono=self.telefono, email=self.email)
	
	@classmethod
	def segretario_al(self, data = datetime.datetime.now()):
		seg = self.objects.filter(ruolo__segretario=True).filter(dipendente_ruolo__data_da__lte=data).exclude(dipendente_ruolo__data_a__lt=data)[0]
		return seg
	
	@classmethod
	def sindaco_al(self, data = datetime.datetime.now()):
		sin = self.objects.filter(ruolo__sindaco=True).filter(dipendente_ruolo__data_da__lte=data).exclude(dipendente_ruolo__data_a__lt=data)[0]
		return sin		
 
	def superiore_al(self, data=datetime.datetime.now()):
		sup = None
		if self.ruolo_al(data).segretario:
			sup = Dipendente.sindaco_al(data)
		elif self.ruolo_al(data).dirigente:
			sup = Dipendente.segretario_al(data)
		elif self.ruolo_al(data).responsabile:
			sup = self.dirigente_al(data)
		else:
			sup = self.responsabile_al(data)
		return sup

	def titolo_it(self, data=datetime.datetime.now()):
		titolo = ""
		ruolo = self.ruolo_al(data)
		femmina = (self.sesso == "F")
		if self.titprinc_it:
			titolo = self.titprinc_it
		elif ruolo.sindaco or ruolo.segretario:
			if femmina:
				titolo = ruolo.nome_it_f
			else:
				titolo = ruolo.nome_it_m
		elif ruolo.dirigente:
			titolo = self.ufficio_al(data).formula_responsabile_it
		elif ruolo.responsabile:
			titolo = self.servizio_al(data).formula_responsabile_it
		else:
			if femmina:
				titolo = self.qualifica_al(data).nome_it_f
			else:
				titolo = self.qualifica_al(data).nome_it_m
		
		return titolo
	
	def titolo_dt(self, data=datetime.datetime.now()):
		titolo = ""
		ruolo = self.ruolo_al(data)
		femmina = (self.sesso == "F")
		if self.titprinc_dt:
			titolo = self.titprinc_dt
		elif ruolo.sindaco or ruolo.segretario:
			if femmina:
				titolo = ruolo.nome_dt_f
			else:
				titolo = ruolo.nome_dt_m
		elif ruolo.dirigente:
			titolo = self.ufficio_al(data).formula_responsabile_dt
		elif ruolo.responsabile:
			titolo = self.servizio_al(data).formula_responsabile_dt
		else:
			if femmina:
				titolo = self.qualifica_al(data).nome_dt_f
			else:
				titolo = self.qualifica_al(data).nome_dt_m
		
		return titolo	

	def mail(self, ml):
		#ml = Mail.objects.get(nome="sgv")
		testo = CompilaMailDip(ml.testo, self)
		oggetto = CompilaMailDip(ml.oggetto, self)
		eml = EmailMultiAlternatives(
			subject=oggetto,
			body=re.sub('[ \t]+', ' ', strip_tags(testo)),
			#from_email='mail.comune.laives.bz.it',
			from_email=ml.mittente,
			to=ml.to.split(";"),
			reply_to=[ml.mittente],
		)
		if ml.cc:
			eml.cc=ml.cc.split(";")
		eml.attach_alternative(testo, "text/html")
		if ml.del_cessazione:
			if self.det_cessazione:
				eml.attach_file(self.det_cessazione.path)
		eml.send()


	@property
	def nomecompleto(self):
		return "{c} {n}".format(c=self.cognome, n=self.nome)
		  
	
	class Meta:
		verbose_name = "Dipendente"
		verbose_name_plural = "Dipendenti"
		ordering = ['cognome', 'nome', ]
	

	# Proxy per visualizzare i dirigenti in AdminPage e rispettivo manager


class DirigentiManager(models.Manager):
	def get_queryset(self):
		return super(DirigentiManager, self).get_queryset().filter(Q(ruolo__dirigente=True)|Q(ruolo__responsabile=True))
	
class Dirigente(Dipendente):
	objects = DirigentiManager()
	class Meta:
		proxy = True
		verbose_name = "Dirigente / responsabile"
		verbose_name_plural = "Dirigenti e Responsabili"
		ordering = ['cognome', 'nome', ]


class Servizio_Ufficio(Date_through_abstract):
	servizio = models.ForeignKey(Servizio, on_delete=models.CASCADE, )
	ufficio = models.ForeignKey(Ufficio, on_delete=models.CASCADE, )

	def __str__(self):
		risultato = ""
		if self.data_a is None:
			txt = "{servizio} - {ufficio} da {data_da:%d/%m/%Y}"
			risultato = txt.format(servizio=self.servizio.nome, ufficio=self.ufficio.nome, data_da=self.data_da)
		else:
			txt = "{servizio} - {ufficio} dal {data_da:%d/%m/%Y} al {data_a:%d/%m/%Y}"
			risultato = txt.format(servizio=self.servizio.nome, ufficio=self.ufficio.nome, data_da=self.data_da, data_a=self.data_a)
		return risultato

	class Meta:
		verbose_name = "Servizio - Ufficio"
		verbose_name_plural = "Servizi - Uffici"

class Dipendente_Ruolo(Dipendente_through_abstract):
	ruolo = models.ForeignKey(Ruolo, on_delete=models.CASCADE, )
	
	def __str__(self):
		risultato = ""
		if self.data_a is None:
			txt = "{cognome} {nome} - {ruolo} dal {data_da:%d/%m/%Y}"
			risultato = txt.format(cognome=self.dipendente.cognome.upper(), nome=self.dipendente.nome, ruolo=self.ruolo.nome, data_da=self.data_da)
		else:
			txt = "{cognome} {nome} - {ruolo} dal {data_da:%d/%m/%Y} al {data_a:%d/%m/%Y}"
			risultato = txt.format(cognome=self.dipendente.cognome.upper(), nome=self.dipendente.nome, ruolo=self.ruolo.nome, data_da=self.data_da, data_a=self.data_a)
		return risultato
	
	class Meta:
		verbose_name = "Dipendente - Ruolo"
		verbose_name_plural = "Dipendenti - Ruoli"

class Dipendente_Qualifica(Dipendente_through_abstract):
	qualifica = models.ForeignKey(Qualifica, on_delete=models.CASCADE, )
	rapportolavoro = models.ForeignKey(RapportoLavoro, on_delete=models.CASCADE, )
	determinato = models.BooleanField("A tempo determinato", default = False, choices=TRUE_FALSE_CHOICES, )

	def __str__(self):
		risultato = ""
		if self.determinato: 
			tag = " (D)"
		else:
			tag = ""
		if self.data_a is None:
			txt = "{cognome} {nome} - {qualifica} {percentuale:1.0%}{determ} dal {data_da:%d/%m/%Y}"
			risultato = txt.format(cognome=self.dipendente.cognome.upper(),nome=(self.dipendente.nome), qualifica=self.qualifica.nome, percentuale=self.rapportolavoro.coefficiente, determ=tag, data_da=self.data_da)
		else:
			txt = "{cognome} {nome} - {qualifica} {percentuale:1.0%}{determ} dal {data_da:%d/%m/%Y} al {data_a:%d/%m/%Y}"
			risultato = txt.format(
				cognome=self.dipendente.cognome.upper(),
				nome=(self.dipendente.nome), 
				qualifica=self.qualifica.nome, 
				percentuale=self.rapportolavoro.coefficiente, 
				determ=tag, 
				data_da=self.data_da, 
				data_a=self.data_a
				)
			
		return risultato

	class Meta:
		verbose_name = "Dipendente - Qualifica"
		verbose_name_plural = "Dipendenti - Qualifiche"
		ordering =['dipendente__cognome', 'dipendente__nome', 'data_da',]

class Dipendente_Qualifica_ModelForm(forms.ModelForm):
	class Meta:
		model = Dipendente_Qualifica
		fields = ('determinato', )
		widgets = {
			'determinato': forms.Select(choices=TRUE_FALSE_CHOICES)
		}

class Dipendente_Servizio(Dipendente_through_abstract):
	servizio = models.ForeignKey(Servizio, on_delete=models.CASCADE, )

	def __str__(self):
		risultato = ""
		if self.data_a is None:
			txt = "{cognome} {nome} - {servizio} dal {data_da:%d/%m/%Y}"
			risultato = txt.format(cognome=self.dipendente.cognome.upper(), nome=self.dipendente.nome, servizio=self.servizio.nome, data_da=self.data_da)
		else:
			txt = "{cognome} {nome} - {servizio} dal {data_da:%d/%m/%Y} al {data_a:%d/%m/%Y}"
			risultato = txt.format(cognome=self.dipendente.cognome.upper(), nome=self.dipendente.nome, servizio=self.servizio.nome, data_da=self.data_da, data_a=self.data_a)
		return risultato
		
	class Meta:
		verbose_name = "Dipendente - Servizio"
		verbose_name_plural = "Dipendenti - Servizi"
	
class Servizio_Responsabile(Date_through_abstract):
	responsabile = models.ForeignKey("Dipendente", on_delete=models.CASCADE, limit_choices_to = {'ruolo__responsabile' : True}, )
	servizio = models.ForeignKey("Servizio", on_delete=models.CASCADE, )
	
	def __str__(self):
		risultato = ""
		if self.data_a is None:
			txt = "{cognome} {nome} - responsabile per: {servizio} dal {data_da:%d/%m/%Y}"
			risultato = txt.format(cognome=self.responsabile.cognome.upper(), nome=self.responsabile.nome, servizio=self.servizio.nome, data_da=self.data_da)
		else:
			txt = "{cognome} {nome} - responsabile per: {servizio} dal {data_da:%d/%m/%Y} al {data_a:%d/%m/%Y}"
			risultato = txt.format(cognome=self.responsabile.cognome.upper(), nome=self.responsabile.nome, servizio=self.servizio.nome, data_da=self.data_da, data_a=self.data_a)
		return risultato
	
	class Meta:
		verbose_name = "Servizio - Responsabile"
		verbose_name_plural = "Servizi - Responsabili"

class Ufficio_Dirigente(Date_through_abstract):
	dirigente = models.ForeignKey("Dipendente", on_delete=models.CASCADE, limit_choices_to = {'ruolo__dirigente' : True}, )
	ufficio = models.ForeignKey("Ufficio", on_delete=models.CASCADE, )

	def __str__(self):
		risultato = ""
		if self.data_a is None:
			txt = "{cognome} {nome} - Dirigente {ufficio} dal {data_da:%d/%m/%Y}"
			risultato = txt.format(cognome=self.dirigente.cognome.upper(), nome=self.dirigente.nome, ufficio=self.ufficio.nome, data_da=self.data_da)
		else:
			txt = "{cognome} {nome} - Dirigente {ufficio} dal {data_da:%d/%m/%Y} al {data_a:%d/%m/%Y}"
			risultato = txt.format(cognome=self.dirigente.cognome.upper(), nome=self.dirigente.nome, ufficio=self.ufficio.nome, data_da=self.data_da, data_a=self.data_a)
		return risultato

	class Meta:
		verbose_name = "Ufficio - Dirigente"
		verbose_name_plural = "Uffici - Dirigenti"
