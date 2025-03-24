from django.db import models
from django.core.mail import send_mail
from datetime import datetime
from babel.dates import format_date

# models TURNI

EMAIL_HOST = "comune-laives-bz-it.mail.protection.outlook.com"
EMAIL_FROM = "volontariato.covid@comune.laives.bz.it"
EMAIL_PORT = 25
EMAIL_SUBJECT = "volontariato / Freiwilligenarbeit test COVID"

TF_MATTINO = 'MA'
TF_POMERIGGIO = 'PO'

TF_CHOICES = [
	(TF_MATTINO, 'Mattino'),
	(TF_POMERIGGIO, 'Pomeriggio'),
]

def mail_avviso(destinatario, nome_completo, data, turno, ruolo, turno_de, ruolo_de):
	data_f = data.strftime("%d-%m-%Y")
	messaggio = 'Buon giorno %s, La avvisiamo che è stato/a selezionato/a per prestare servizio il giorno %s nella fascia oraria %s, con il ruolo di %s.\r\n\r\n' % (nome_completo, data_f, turno, ruolo)
	messaggio += 'Per confermare la propria disponibilità o qualora fosse impossibilitato/a a prestare servizio, La preghiamo di avvisarci quanto prima contattando il numero 0471 595800 o scrivendo una e-mail a volontariato.covid@comune.laives.bz.it.\r\n\r\n Grazie per la preziosa collaborazione.\r\n\r\n'
	messaggio += " ---------------------------------------- \r\n\r\n" 
	messaggio += 'Guten Morgen, %s. Wir teilen Ihnen mit, dass Sie ausgewählt wurden, am %s, %s als %s Dienst zu leisten. \r\n\r\n' % (nome_completo, data_f, turno_de, ruolo_de)
	messaggio += 'Um den genannten Dienst zu bestätigen oder Sollte es Ihnen nicht möglich sein, den Dienst durchzuführen, sind Sie gebeten dies sobald wie möglich unter der Nr. 0471 595800 oder mittels E-Mail an freiwilligenarbeit.covid@gemeinde.leifers.bz.it mitzuteilen.\r\n\r\n Danke für Ihre Zusammenarbeit.'
	res = send_mail(subject= EMAIL_SUBJECT, message= messaggio, from_email= EMAIL_FROM, recipient_list= (destinatario, ), fail_silently= False)	
	return res

# Create your models here.

class Fascia(models.Model):
	nome = models.CharField("Abbreviazione", max_length= 5, primary_key=True, )
	descrizione = models.CharField("Descrizione della Fascia Oraria", max_length=200, null=True, blank=True, )
	desc_breve = models.CharField("Descrizione breve per tabella", max_length=20, null=True, blank=True, )
	descrizione_de = models.CharField("Descrizione della Fascia Oraria (Tedesco)", max_length=200, null=True, blank=True, )
	tipo = models.CharField('Tipo di fascia oraria', max_length=2, choices=TF_CHOICES, default=TF_MATTINO, )
	ordine = models.IntegerField("Indice di ordinamento", default=0, )
	def __str__(self):
		return '%s' % (self.descrizione)
	
	def tipo_fascia(self):
		return '%s' % self.desc_breve
		
	class Meta:
		verbose_name = "Fascia oraria"
		verbose_name_plural = "Fasce orarie"
		ordering = ['ordine']


class Ruolo(models.Model):
	nome = models.CharField("Abbreviazione", max_length= 3, primary_key=True, )
	descrizione = models.TextField("Descrizione del ruolo", null=True, blank=True, )
	descrizione_de = models.TextField("Descrizione del ruolo (Tedesco)", null=True, blank=True, )
	colore = models.CharField("Codice esadecimale colore", default="#000000", max_length=7,)
	ordine = models.IntegerField("Indice di ordinamento", default=0, )
	richiesti = models.CharField("Numero di persone richieste per il ruolo", max_length= 12, null=True, blank=True, )

	def __str__(self):
		return '%s' % (self.descrizione)
		
	class Meta:
		verbose_name = "Ruolo"
		verbose_name_plural = "Ruoli"
		ordering = ['ordine']

		
class Persona(models.Model):
	id = models.AutoField("Codice Identificativo", primary_key=True, )
	nome = models.CharField("Nome", max_length= 40, )
	cognome = models.CharField("Cognome", max_length= 40, )
	email = models.CharField("E-mail", max_length= 100, null=True, blank=True)
	telefono = models.CharField("Telefono", max_length= 40, null=True, blank=True)
	note = models.TextField("Note aggiuntive", null=True, blank=True)
	disponibilita = models.ManyToManyField(Fascia, )
	capacita = models.ManyToManyField(Ruolo, )
	
	def __str__(self):
		return '%s %s' % (self.cognome.upper(), self.nome)
		
	def nome_completo(self):
		return '%s %s' % (self.cognome.upper(), self.nome.lower().capitalize())

	def nome_html(self):
		return '<p>%s %s</p>' % (self.cognome.upper(), self.nome.lower().capitalize())
		
	class Meta:
		verbose_name = "Persona"
		verbose_name_plural = "Persone"
		
	
class Giorno(models.Model):
	id = models.AutoField(primary_key=True, )
	data = models.DateField("Giorno", unique=True, )
	note = models.CharField("Annotazioni", max_length=200, null=True, blank=True, )

	def __str__(self):
#		return '%s' % (self.data.strftime("%a %d-%m-%Y"))
		return '%s' % format_date(self.data, format="EEE, d-MMM-yyyy", locale='it_IT')	
	def data_giorno(self):
		return '%s' % (self.data.strftime("%a %d-%m-%Y"))
		
	class Meta:
		verbose_name = "Giorno"
		verbose_name_plural = "Giorni"
		ordering =['data']
		
#	def avvisa(self):
#		for tu in self__turno.objects.all()
#			tu.avvisa()
		
class Turno(models.Model):
	giorno = models.ForeignKey(Giorno, on_delete=models.CASCADE, )
	fascia = models.ForeignKey(Fascia, on_delete=models.CASCADE, )
	ruolo = models.ForeignKey(Ruolo, on_delete=models.CASCADE, )
	persona = models.ForeignKey(Persona, on_delete=models.CASCADE, )
	avvisato = models.BooleanField('Persona Avvisata', default=False)
	confermato = models.BooleanField('Turno confermato', default=False)
		
	def __str__(self):
		return '%s [%s %s] => %s' % (self.giorno, self.fascia, self.ruolo, self.persona)
		
	class Meta:
		verbose_name = "Turno assegnato"
		verbose_name_plural = "Turni assegnati"
#		unique_together =('giorno', 'fascia', 'ruolo', )
	
	def avvisa(self):
		mail_avviso(self.persona.email, self.persona, self.giorno.data, self.fascia.descrizione, self.ruolo.descrizione, self.fascia.descrizione_de, self.ruolo.descrizione_de)
		
	