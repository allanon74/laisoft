from django.db import models

# Models PERSONALE
# Create your models here.

# Classi Astratte

class Base_abstract(models.Model):
	id = models.AutoField("Codice Identificativo", primary_key=True, )
	class Meta:
		abstract = True

class Date_through_abstract(Base_abstract):
	data_da = models.DateField("Data di inizio", )
	data_a = models.DateField("Data di fine", null=True, blank = True, )
	#note = models.TextField("Annotazioni", null=True, blank=True, )
	
	class Meta:
		ordering = ['data_da', ]
		abstract = True

class Multi_abstract(Base_abstract):
	nome = models.CharField("Nome Breve", max_length= 20, )
	nome_it_m = models.CharField("Nome italiano maschile", max_length= 40, )
	nome_it_f = models.CharField("Nome italiano femminile", max_length= 40, null=True, blank = True, )
	nome_dt_m = models.CharField("Nome tedesco maschile", max_length= 40, null=True, blank = True, )
	nome_dt_f = models.CharField("Nome tedesco femminile", max_length= 40, null=True, blank = True, )
	
	def __str__(self):
		return self.nome
	class Meta:
		abstract = True


class Dipendente_through_abstract(Date_through_abstract):
	dipendente = models.ForeignKey("Dipendente", on_delete=models.CASCADE, )
	
	class Meta:
		abstract = True

# Classi Reali

class Ruolo(Multi_abstract):
	dirigente = models.BooleanField("Ruolo dirigenziale", default=False, )
	coordinatore = models.BooleanField("Ruolo di coordinamento", default=False, )
	responsabile = models.BooleanField("Ruolo di responsabile", default=False, )
	segretario = models.BooleanField("Ruolo segretario generale", default=False, )
	ammsistema = models.BooleanField("Ruolo amministratore di sistema", default=False, )
	sindaco = models.BooleanField("Ruolo da sindaco", default=False, )
	
	class Meta:
		verbose_name = "Ruolo"
		verbose_name_plural = "Ruoli"
		ordering = ['nome', ]

class Livello(Base_abstract):
	livello = models.CharField("Livello", max_length= 10, )
	indice = models.IntegerField("Indice", )
	coefficiente = models.IntegerField("Coefficiente premio produzione", )
	
	def __str__(self):
		return self.livello
	
	class Meta:
		verbose_name = "Livello"
		verbose_name_plural = "Livelli"
		ordering = ['indice', ]

class Qualifica(Multi_abstract):
	livello = models.ForeignKey('Livello', on_delete=models.CASCADE, verbose_name="Livello", )
	class Meta:
		verbose_name = "Qualifica"
		verbose_name_plural = "Qualifiche"
		ordering = ['nome', ]

class Ufficio(Multi_abstract):

	dirigente = models.ManyToManyField(
		"Dipendente",
		related_name = "dirigente",
		through='Ufficio_Dirigente',
		through_fields = ('ufficio', 'dirigente'),
	)

	class Meta:
		verbose_name = "Ufficio"
		verbose_name_plural = "Uffici"
		ordering = ['nome', ]

class Servizio(Multi_abstract):
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

	class Meta:
		verbose_name = "Servizio"
		verbose_name_plural = "Servizi"
		ordering = ['nome', ]


class Dipendente(models.Model):
	id = models.AutoField("Codice Identificativo", primary_key=True, )
	nome = models.CharField("Nome", max_length= 40, )
	cognome = models.CharField("Cognome", max_length= 40, )
	userid = models.CharField("Nome Utente", max_length= 16, null=True, blank=True, )
	email = models.CharField("E-mail", max_length= 100, null=True, blank=True)
	telefono = models.CharField("Telefono", max_length= 40, null=True, blank=True)
	cellulare = models.CharField("Cellulare", max_length= 40, null=True, blank=True)
	catprotetta = models.BooleanField("Categoria Protetta", default=False, )
	note = models.TextField("Note aggiuntive", null=True, blank=True)
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
	
	def __str__(self):
		return '%s %s' % (self.cognome.upper(), self.nome)
	
	class Meta:
		verbose_name = "Dipendente"
		verbose_name_plural = "Dipendenti"
		ordering = ['cognome', 'nome', ]

class Servizio_Ufficio(Date_through_abstract):
	servizio = models.ForeignKey(Servizio, on_delete=models.CASCADE, )
	ufficio = models.ForeignKey(Ufficio, on_delete=models.CASCADE, )
	# dirigente = models.ForeignKey("Dipendente", on_delete=models.CASCADE, limit_choices_to = {'ruolo__dirigente' : True}, )
	# dirigente = models.ForeignKey("Dipendente", on_delete=models.CASCADE, )

class Dipendente_Ruolo(Dipendente_through_abstract):
	ruolo = models.ForeignKey(Ruolo, on_delete=models.CASCADE, )
	
	class Meta:
		verbose_name = "Dipendente - Ruolo"
		verbose_name_plural = "Dipendenti - Ruoli"

class Dipendente_Qualifica(Dipendente_through_abstract):
	qualifica = models.ForeignKey(Qualifica, on_delete=models.CASCADE, )

	class Meta:
		verbose_name = "Dipendente - Qualifica"
		verbose_name_plural = "Dipendenti - Qualifiche"

class Dipendente_Servizio(Dipendente_through_abstract):
	servizio = models.ForeignKey(Servizio, on_delete=models.CASCADE, )

	class Meta:
		verbose_name = "Dipendente - Servizio"
		verbose_name_plural = "Dipendenti - Servizi"
	
class Servizio_Responsabile(Date_through_abstract):
	responsabile = models.ForeignKey("Dipendente", on_delete=models.CASCADE, limit_choices_to = {'ruolo__responsabile' : True}, )
	servizio = models.ForeignKey("Servizio", on_delete=models.CASCADE, )
	
	class Meta:
		verbose_name = "Servizio - Responsabile"
		verbose_name_plural = "Servizi - Responsabili"

class Ufficio_Dirigente(Date_through_abstract):
	dirigente = models.ForeignKey("Dipendente", on_delete=models.CASCADE, limit_choices_to = {'ruolo__dirigente' : True}, )
	ufficio = models.ForeignKey("Ufficio", on_delete=models.CASCADE, )

	class Meta:
		verbose_name = "Ufficio - Dirigente"
		verbose_name_plural = "Uffici - Dirigenti"
