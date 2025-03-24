from django.db import models
from django.db.models import Avg
from django.db.models import Q
#from django.core.urlresolvers import reverse
from django.utils.html import mark_safe
from django.utils.timezone import now
from dipendenti.models import Dipendente
import dipendenti
import datetime
from pytz import timezone

from simple_history.models import HistoricalRecords

# Models VALUTAZIONI

TZ = timezone("Europe/Rome")

BASE_URL="http://leifersdjango.leifers.gvcc.net/valutazioni/"

class Base_abstract(models.Model):
	id = models.AutoField("Codice Identificativo", primary_key=True, )
	class Meta:
		abstract = True

class Anno(Base_abstract):
	anno = models.IntegerField("Anno di riferimento", )
	
	def __str__(self):
		txt = "Anno {anno}"
		return txt.format(anno=self.anno, )
	
	class Meta:
		verbose_name = "Anno"
		verbose_name_plural = "Anni"
	
class Voto(Base_abstract):
	valore = models.IntegerField("Valore della votazione", )
	descrizione_it = models.CharField("Giudizio in italiano", max_length = 30, )
	descrizione_td = models.CharField("Giudizio in tedesco", max_length = 30, )
	desc_estesa_it = models.TextField("Descrizione in italiano", null= True, blank=True,)
	desc_estesa_td = models.TextField("Descrizione in tedesco", null= True, blank=True,)
	
	def __str__(self):
		txt = "{giudizio} ({voto})"
		return txt.format(giudizio=self.descrizione_it, voto=self.valore)
	
	class Meta:
		verbose_name = "Voto"
		verbose_name_plural = "Voti"
	
class TipoValutazione(Base_abstract):
	nome = models.CharField("Nome del tipo di valutazione", max_length = 50, )
	descrizione_it = models.TextField("Descrizione estesa del tipo di valutazione in italiano", null=True, blank=True, )
	descrizione_td = models.TextField("Descrizione estesa del tipo di valutazione in tedesco", null=True, blank=True, )
	sezione = models.CharField("Sezione di valutazione", max_length = 1, )
	indice = models.IntegerField("Indice di ordinamento", )
	peso = models.DecimalField("Peso della valutazione per dipendenti",decimal_places=2, max_digits= 5, default=0.3, )
	peso_coord = models.DecimalField("Peso della valutazione per coordinatori e responsabili", decimal_places=2, max_digits= 5, default=0.2, )
	
	
	def __str__(self):
		txt = "{valutazione}"
		return txt.format(valutazione=self.nome)
	
	class Meta:
		verbose_name = "Tipo di valutazione"
		verbose_name_plural = "Tipi di valutazione"
		ordering = ['indice', 'nome', ]

class CategoriaElementi(Base_abstract):
	indice = models.IntegerField("indice della voce", default=0)
	descrizione_it = models.CharField("Descrizione in italiano", max_length = 100, )
	descrizione_td = models.CharField("Descrizione in tedesco", max_length = 100, )
	
	def __str__(self):
		txt = "{indice}. {desc}"
		return txt.format(indice=self.indice, desc = self.descrizione_it)	
	
	class Meta:
		verbose_name = "Categoria di elementi di valutazione"
		verbose_name_plural = "Categorie di elementi di valutazione"

class Elemento(Base_abstract):
	indice = models.IntegerField("indice della voce", default=0)
	tipo_valutazione = models.ForeignKey(TipoValutazione, on_delete = models.CASCADE, verbose_name = "Sezione della valutazione", )
	descrizione_it = models.CharField("Descrizione in italiano", max_length = 100, )
	descrizione_td = models.CharField("Descrizione in tedesco", max_length = 100, )
	categoria = models.ForeignKey(CategoriaElementi, on_delete=models.CASCADE, verbose_name = "Categoria dell'elemento", null=True, blank=True,)
	
	

	def __str__(self):
		txt = "{sez}{indice}. {desc}"
		return txt.format(indice=self.indice, sez = self.tipo_valutazione.sezione, desc = self.descrizione_it)
		
	class Meta:
		verbose_name = "Elemento di valutazione"
		verbose_name_plural = "Elementi di valutazione"
		ordering = ['indice', ]




class Formulario_Obiettivo(Base_abstract):
	formulario = models.ForeignKey("Formulario", on_delete=models.CASCADE, )
	obiettivo = models.ForeignKey(Elemento, on_delete=models.CASCADE, limit_choices_to = Q(tipo_valutazione__sezione__iexact="a"), default=1, )
	descrizione = models.CharField("Descrizione dell'obiettivo", max_length=100, )
	risultato = models.CharField("Risultato del conseguimento dell'obiettivo", max_length=150, null=True, blank=True, )
	voto = models.ForeignKey(Voto, on_delete=models.CASCADE, null=True, blank=True, )

	
	class Meta:
		unique_together = ['formulario','obiettivo', 'descrizione']
		verbose_name = "Obiettivo annuale."
#		verbose_name_plural = "Tra il dipendente ed il diretto superiore deve essere fissato almeno un obiettivo annuale."
		verbose_name_plural = "Obiettivi annuali (1+)"
	
class Formulario_Prestazione(Base_abstract):
	formulario = models.ForeignKey("Formulario", on_delete=models.CASCADE, )
	prestazione = models.ForeignKey(Elemento, on_delete=models.CASCADE, limit_choices_to = Q(tipo_valutazione__sezione__iexact="b"), )
	voto = models.ForeignKey(Voto, on_delete=models.CASCADE, null=True, blank=True, )
	
	class Meta:
		unique_together = ['formulario','prestazione']
		verbose_name = "Criterio di prestazione"
#		verbose_name_plural = "Tra il dipendente ed il diretto superiore devono essere fissati a priori 7 criteri di prestazioni da valutare."
		verbose_name_plural = "Prestazioni (7)"

class Formulario_Sociale(Base_abstract):
	formulario = models.ForeignKey("Formulario", on_delete=models.CASCADE, )
	sociale = models.ForeignKey(Elemento, on_delete=models.CASCADE, limit_choices_to = Q(tipo_valutazione__sezione__iexact="c"), verbose_name="Competenza sociale", )
	voto = models.ForeignKey(Voto, on_delete=models.CASCADE, null=True, blank=True, )

	class Meta:
		unique_together = ['formulario', 'sociale']
		verbose_name = "Criterio di competenza sociale"
#		verbose_name_plural = "Tra il dipendente ed il diretto superiore devono essere fissati a priori 3 criteri di competenze sociali da valutare."
		verbose_name_plural = "Sociali (3)"

class Formulario_Coordinamento(Base_abstract):
	formulario = models.ForeignKey("Formulario", on_delete=models.CASCADE, )
	coordinamento = models.ForeignKey(Elemento, on_delete=models.CASCADE, limit_choices_to = Q(tipo_valutazione__sezione__iexact="d"), verbose_name="Competenza di coordinamento", )
	voto = models.ForeignKey(Voto, on_delete=models.CASCADE, null=True, blank=True, )

	class Meta:
		unique_together = ['formulario', 'coordinamento']
		verbose_name = "Criterio di Coordinamento"
		verbose_name_plural = "SOLO COORDINATORI. Tra il dipendente ed il diretto superiore devono essere fissati a priori 2 criteri di competenze direttive o di coordinamento da valutare."
		verbose_name_plural = "SOLO COORDINATORI (2)"
		

class Firma(Base_abstract):
	dipendente = models.ForeignKey(Dipendente, on_delete=models.CASCADE, verbose_name='Utente firmatario',)
	formulario = models.ForeignKey("Formulario", on_delete=models.CASCADE, verbose_name = "Formulario in firma", )
	data_firma = models.DateTimeField("Data di firma", auto_now=True, )
	tipo_formulario = models.CharField("Tipo di Formulario",max_length=12 , default="Obiettivi",)
	note = models.TextField("Note del dipendente", null=True, blank=True, )
	
	class Meta:
		verbose_name = "Firma"
		verbose_name_plural = "Firme"
		
	def __str__(self):
		text = "Firmato il {data_f:%d/%m/%Y alle ore %H:%M} da {nome_d} {cognome_d}"
		return text.format(data_f = self.data_firma.astimezone(TZ), nome_d=self.dipendente.nome, cognome_d=self.dipendente.cognome)
	
	def firma_testo(self):
		text = "Firmato elettronicamente il {data_f:%d/%m/%Y alle ore %H:%M} \nda {cognome_d} {nome_d}"
		return text.format(data_f = self.data_firma.astimezone(TZ), nome_d=self.dipendente.nome, cognome_d=self.dipendente.cognome)
	
	def firma_testo_de(self):
		text = "Elektronisch unterzeichnet am {data_f:%d/%m/%Y um %H:%M} Uhr \nvon {cognome_d} {nome_d}"
		return text.format(data_f = self.data_firma.astimezone(TZ), nome_d=self.dipendente.nome, cognome_d=self.dipendente.cognome)


	
class Formulario(Base_abstract):
	anno = models.ForeignKey(Anno, on_delete=models.CASCADE, verbose_name="Anno di riferimento", )
	dipqual = models.ForeignKey(
		dipendenti.models.Dipendente_Qualifica, 
		on_delete=models.CASCADE, 
		verbose_name = "Dipendente valutato",
#		limit_choices_to = Q()
	)
	data_obiettivo = models.DateField(verbose_name="Data di DISCUSSIONE criteri ed obiettivi", default=now, )
	data_valutazione = models.DateField(verbose_name="Data di VALUTAZIONE criteri ed obiettivi", null=True, blank=True, )
	note = models.TextField(verbose_name="Note del dipendente", null=True, blank=True,)
	logo = models.ForeignKey(dipendenti.models.Logo, on_delete=models.CASCADE, verbose_name='logo del modello', default=1)
	data_modifica = models.DateTimeField("Data ultima modifica", auto_now=True, )

	
	
	obiettivi = models.ManyToManyField(
	Elemento,
	related_name="obiettivi",
	through = Formulario_Obiettivo,
	through_fields = ('formulario', 'obiettivo'),
	help_text = "Tra il dipendente ed il diretto superiore deve essere fissato almeno un obiettivo annuale.",
	)
	
	prestazioni = models.ManyToManyField(
	Elemento,
	related_name="prestazioni",
	through = Formulario_Prestazione,
	through_fields = ('formulario', 'prestazione'),
	help_text = "Tra il dipendente ed il diretto superiore devono essere fissati a priori 7 criteri di prestazioni da valutare.",
	)
	
	sociali = models.ManyToManyField(
	Elemento,
	related_name="sociali",
	through = Formulario_Sociale,
	through_fields = ('formulario', 'sociale'),
	help_text = "Tra il dipendente ed il diretto superiore devono essere fissati a priori 3 criteri di competenze sociali da valutare.",
	)
	
	coordinamenti = models.ManyToManyField(
	Elemento,
	related_name="coordinamenti",
	through = Formulario_Coordinamento,
	through_fields = ('formulario', 'coordinamento'),
	help_text = "Tra il dipendente ed il diretto superiore devono essere fissati a priori 2 criteri di competenze direttive o di coordinamento da valutare.",
	)
	
	firme = models.ManyToManyField(
		Dipendente, 
		related_name = "formulari",
		through = Firma,
		through_fields = ("formulario", "dipendente"),
		help_text = "Elenco firme"
		)
	
	history = HistoricalRecords(m2m_fields=[obiettivi, prestazioni, sociali, coordinamenti, firme])
	
	def testo_firma(self):
		fms = Firma.objects.filter(formulario = self.id).order_by('-data_firma')
		txt = ""
		if fms.count() > 0:
			if fms[0].data_firma > self.data_modifica:
				txt = fms[0].firma_testo()
			else:
				txt = "FIRMA ELETTRONICA NON PRESENTE"
		else:
			txt = "FIRMA ELETTRONICA NON PRESENTE"
		return txt
	
	def testo_firma_de(self):
		fms = Firma.objects.filter(formulario = self.id).order_by('-data_firma')
		txt = ""
		if fms.count() > 0:
			if fms[0].data_firma > self.data_modifica:
				txt = fms[0].firma_testo_de()
			else:
				txt = "ELEKTRONISCHE UNTERSCHRIFT NICHT VORHANDEN"
		else:
			txt = "ELEKTRONISCHE UNTERSCHRIFT NICHT VORHANDEN"
		return txt
	
	def firmato(self):
		
		fms = Firma.objects.filter(formulario = self.id).order_by('-data_firma')
		res = False
		if fms.count()>0:
			if fms[0].data_firma > self.data_modifica:
				res = True
				
		return res
	
	def firma(self):
		fms = Firma.objects.filter(formulario = self.id).order_by('-data_firma')
		if fms.count()>0:
			return fms[0]
		else:
			return None
	
	def media(self, sez):
		
		data = datetime.date(2000,1,1)
		if self.dipqual.data_a is None:
			data = datetime.date(self.anno.anno, 12, 31)
		else:
			data = min(self.dipqual.data_a, datetime.date(self.anno.anno, 12, 31))
		
		md = float(99)
		if sez == "A":
			med = Formulario_Obiettivo.objects.filter(formulario__exact=self.id).aggregate(Avg('voto__valore'))
		elif sez == "B":
			med = Formulario_Prestazione.objects.filter(formulario__exact=self.id).aggregate(Avg('voto__valore'))
		elif sez == "C":
			med = Formulario_Sociale.objects.filter(formulario__exact=self.id).aggregate(Avg('voto__valore'))
		elif sez == "D":
			med = Formulario_Coordinamento.objects.filter(formulario__exact=self.id).aggregate(Avg('voto__valore'))
		
		if med['voto__valore__avg'] is None:
			return None
		else:
			md = med['voto__valore__avg']
			coeff = float(1)
			if self.dipqual.dipendente.ruolo_al(data).responsabile == True:
				coeff = float(TipoValutazione.objects.filter(sezione=sez)[0].peso_coord)
			else:
				coeff = float(TipoValutazione.objects.filter(sezione=sez)[0].peso)
			return md * coeff
	
	def media_a(self):
		return self.media("A")
	
	def media_b(self):
		return self.media("B")
	
	def media_c(self):
		return self.media("C")
	
	def media_d(self):
		return self.media("D")
	
	def stampa_italiano(self):
		txt = "<a href={url}/stampaformulario/{id}/>Stampa formulario in italiano</a>"
		return mark_safe(txt.format(url=BASE_URL, id=self.id))
	stampa_italiano.short_description = 'Stampa in italiano'
	
	def tipo(self):
		desc = ""
		if self.data_valutazione is None:
			desc = "Obiettivi"
		else:
			desc = "Valutazione"
		return desc
	
	def __str__(self):
		txt = "Formulario di {cognome} {nome} per l'anno {anno}"
		return txt.format(cognome=self.dipqual.dipendente.cognome.upper(), nome=self.dipqual.dipendente.nome, anno=self.anno.anno)

	class Meta:
		unique_together = ['anno', 'dipqual']
		verbose_name = "Formulario di valutazione annuale"
		verbose_name_plural = "Formulari di valutazione annuali"
