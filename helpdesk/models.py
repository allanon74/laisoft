from django.db import models
from django.db.models import Q
from dipendenti.models import Dipendente
from django.conf import settings

from django.core.mail import EmailMessage
from django.utils.html import format_html


TESTO_EMAIL_TICKET_AZIONE = "Buon giorno, {persona}.\r\n\r\n"
TESTO_EMAIL_TICKET_AZIONE += "È stata svolta una nuova attività sul tuo ticket {ticket}.\r\n\r\n"
TESTO_EMAIL_TICKET_AZIONE += "Agente: {agente_azione}\r\n"
TESTO_EMAIL_TICKET_AZIONE += "Azione: {azione}\r\n\r\n\r\n"
TESTO_EMAIL_TICKET_AZIONE += "per controllare i tuoi ticket: {base_url}helpdesk/lista/"

TESTO_EMAIL_TICKET_APERTURA = "Buon giorno, {persona}.\r\n\r\n"
TESTO_EMAIL_TICKET_APERTURA += "È stato aperto il ticket di intervento {ticket} a tuo nome da {agente_apertura} il {data_apertura}.\r\n"
TESTO_EMAIL_TICKET_APERTURA += "Richiesta: {testo_apertura}\r\n\r\n"
TESTO_EMAIL_TICKET_APERTURA += "Il ticket verrà gestito quanto prima dal servizio informatica.\r\n\r\n"
TESTO_EMAIL_TICKET_APERTURA += "per controllare i tuoi ticket: {base_url}helpdesk/lista/"

TESTO_EMAIL_TICKET_CHIUSURA = "Buon giorno, {persona}.\r\n\r\n"
TESTO_EMAIL_TICKET_CHIUSURA += "Siamo lieti di comunicare che il suo ticket di intervento tecnico {ticket} è stato risolto.\r\n\r\n"
TESTO_EMAIL_TICKET_CHIUSURA += "Data della soluzione: {data_chiusura}\r\n"
TESTO_EMAIL_TICKET_CHIUSURA += "Autore della soluzione: {agente_chiusura}\r\n"
TESTO_EMAIL_TICKET_CHIUSURA += "Soluzione:\r\n\r\n {soluzione} \r\n\r\n"
TESTO_EMAIL_TICKET_CHIUSURA += "per controllare i tuoi ticket: {base_url}helpdesk/lista/"

TESTO_HELP = "{persona} titolare del ticket <br />"
TESTO_HELP += "{ticket} id del ticket<br />"
TESTO_HELP += "{agente_azione} incaricato che inoltra l'azione<br />"
TESTO_HELP += "{data_azione} data di inserimento dell'azione'<br />"
TESTO_HELP += "{azione} testo dell'azione svolta<br />"
TESTO_HELP += "{agente_apertura} incaricato che apre il ticket<br />"
TESTO_HELP += "{data_apertura} data di apertura del ticket<br />"
TESTO_HELP += "{testo_apertura} testo del ticket inserito<br />"
TESTO_HELP += "{data_chiusura} data di chiusura del ticket<br />"
TESTO_HELP += "{agente_chiusura} incaricato che ha concluso il ticket<br />"
TESTO_HELP += "{soluzione} testo della risoluzione del ticket<br />"
TESTO_HELP += "{base_url} URL base del server"



EMAIL_ADMIN = "edp@comune.laives.bz.it"
EMAIL_SENDER = "edp_leifers@comune.laives.bz.it"

TITOLO_EMAIL_AZIONE = "{ticket}: nuova azione."
TITOLO_EMAIL_APERTURA = "{ticket}: Nuovo Ticket creato."
TITOLO_EMAIL_CHIUSURA = "{ticket}: Ticket Risolto."

def datetime_format(data):
	testo = "{dt:%d.%m.%Y alle ore %H:%M}"
	res = ""
	if data:
		res = testo.format(dt=data)
	return res

def formatta_testo_ticket (testo, ticket):
	
	ag_c = ""
	if ticket.utente_chiusura:
		ag_c = ticket.utente_chiusura.last_name + " " + ticket.utente_chiusura.first_name
	
	res = format_html(
		testo.format(
			persona = ticket.persona.cognome + " " + ticket.persona.nome,
			ticket = ticket.nome,
			agente_azione = "na",
			data_azione = "na",
			azione = "na",
			agente_apertura = ticket.utente_apertura.last_name + " " + ticket.utente_apertura.first_name,
			data_apertura = datetime_format(ticket.data_apertura),
			testo_apertura = ticket.testo,
			data_chiusura = datetime_format(ticket.data_chiusura),
			agente_chiusura = ag_c,
			soluzione = ticket.soluzione,
			base_url = settings.BASE_URL,
			)
		)
	
	return res
	
def formatta_testo_azione(testo, azione):
	
	ag_c = ""
	if azione.ticket.utente_chiusura:
		ag_c = azione.ticket.utente_chiusura.last_name + " " + azione.ticket.utente_chiusura.first_name
	
	res = format_html(
		testo.format(
			persona = azione.ticket.persona.cognome + " " +azione.ticket.persona.nome,
			ticket = azione.ticket.nome,
			agente_azione = azione.utente,
			data_azione = datetime_format(azione.data_azione),
			azione = azione.nota,
			agente_apertura = azione.ticket.utente_apertura.last_name + " " + azione.ticket.utente_apertura.first_name,
			data_apertura = datetime_format(azione.ticket.data_apertura),
			testo_apertura = azione.ticket.testo,
			data_chiusura = datetime_format(azione.ticket.data_chiusura),
			agente_chiusura =ag_c,
			soluzione = azione.ticket.soluzione,
			base_url = settings.BASE_URL,
			)
		)
	
	return res


# Create your models here.

class Base_abstract(models.Model):
	id = models.AutoField("Codice Identificativo", primary_key=True, )
	class Meta:
		abstract = True
		
class counter(models.Model):
	id = models.CharField('ID del contatore', max_length=2, primary_key=True,)
	valore = models.IntegerField('valore del contatore')
	
	def __str__(self):
		text = "{id}: {val}"
		return text.format(id=self.id,val=self.valore)
	
	def next(id_contatore):
		val = -99
		if counter.objects.filter(id=id_contatore).count() == 0:
			cnt = counter(id=id_contatore, valore=1)
			val = 1
			cnt.save()
		else:
			cnt = counter.objects.get(id=id_contatore)
			val = cnt.valore + 1
			cnt.valore = val
			cnt.save()
		return val
	
	class Meta:
		verbose_name = "Contatore"
		verbose_name_plural = "Contatori"
		
class GruppoSupporto(Base_abstract):
	nome = models.CharField('Nome del gruppo', max_length=30)
	membri = models.ManyToManyField(
		Dipendente,
		)
#	email = models.TextField("Testo e-mail", default=TESTO_EMAIL_TICKET_AZIONE)
	
	def __str__(self):
		text = "Gruppo {nom}"
		return text.format(nom=self.nome) 
	
	class Meta:
		verbose_name = "Gruppo di supporto"
		verbose_name_plural = "Gruppi di supporto"

class Tipologia(Base_abstract):
	nome = models.CharField('Nome della tipologia', max_length=30)
	sigla = models.CharField('Sigla della tipologia (2 caratteri)', max_length = 2)
	descrizione = models.TextField('Descrizione', null=True, blank=True, )
	gruppo = models.ForeignKey(GruppoSupporto, on_delete=models.CASCADE, verbose_name="Gruppo incaricato", )
	principale = models.BooleanField("Tipologia primaria", default=False,)
	email_apertura = models.TextField(
		"Testo e-mail apertura ticket", 
		default=TESTO_EMAIL_TICKET_APERTURA,
		help_text=TESTO_HELP
		)
	email_azione = models.TextField(
		"Testo e-mail azione pubblica", 
		default=TESTO_EMAIL_TICKET_AZIONE,
		help_text=TESTO_HELP
								 )
	email_chiusura = models.TextField(
		"Testo e-mail chiusura ticket", 
		default=TESTO_EMAIL_TICKET_CHIUSURA,
		help_text=TESTO_HELP
		)
	
	
	def __str__(self):
		text = "{nom} ({sig})"
		return text.format(nom = self.nome, sig = self.sigla)
	
	class Meta:
		verbose_name = "Tipologia di supporto"
		verbose_name_plural = "Tipologie di supporti"
		
class Ticket(Base_abstract):
	nome = models.CharField('ID ticket', max_length=12, unique=True, )
	tipologia = models.ForeignKey(Tipologia, on_delete=models.CASCADE, verbose_name="Tipologia di problema", )
	persona = models.ForeignKey(Dipendente, on_delete=models.CASCADE, verbose_name='Persona richiedente',)
	incaricato = models.ForeignKey(Dipendente, on_delete=models.CASCADE, verbose_name='Incaricato', related_name="ticket_in_carico", null=True, blank=True,)
	testo = models.TextField('Descrizione del problema', )
	data_apertura = models.DateTimeField(auto_now_add=True, )
	data_modifica = models.DateTimeField(auto_now=True, )
	data_chiusura = models.DateTimeField(null=True, blank=True,)
	utente_apertura = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='ticket_aperti', on_delete=models.CASCADE, verbose_name='utente di apertura ticket',)
	utente_modifica = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='ticket_modificati', on_delete=models.CASCADE, verbose_name='utente ultima modifica',null=True, blank=True,)
	utente_chiusura = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='ticket_chiusi', on_delete=models.CASCADE, verbose_name='utente chiusura ticket',null=True, blank=True,)
	note = models.TextField('Note Interne', null=True, blank=True,)
	soluzione = models.TextField('Soluzione', null=True, blank=True,)
	chiuso = models.BooleanField("Ticket chiuso", default = False,)
	
	def __str__ (self):
		text = "{nome} - {cog} {dt:%d/%m/%Y}"
		return text.format(nome = self.nome, cog = self.persona.cognome, dt = self.data_apertura)
	
	def save(self, *args, **kwargs):
		mail_c = False
		mail_s = False
		if not hasattr(self, 'nome') or self.nome == "":
			idtype = self.tipologia.sigla
			
			txt = "{id}"
			
			txt = txt.format(id=counter.next(idtype)).rjust(10,'0')
			txtnome = "{grp}{num}"
			self.nome = txtnome.format(grp=idtype, num=txt)

		if not self.pk:
			mail_c = True
			
		if self.soluzione:
			mail_s = True
			
		super(Ticket, self).save(*args, **kwargs)
		if mail_c:
			self.mail_apertura()
		if mail_s:
			self.mail_chiusura()
	
	def mail_apertura(self):
#		testo = format_html(self.tipologia.email_apertura, 
#					  self.persona, 
#					  self.utente_apertura.last_name + " " + self.utente_apertura.first_name, 
#					  datetime_format(self.data_apertura)
#					  	)

		testo = formatta_testo_ticket(self.tipologia.email_apertura, self)
		mittente = EMAIL_SENDER
				
		destinatari = [self.persona.email,] 
		bcc_list = []
		for ut in self.tipologia.gruppo.membri.all():	
			bcc_list.append(ut.email)
		
		if len(destinatari) == 0:
			destinatari = [EMAIL_ADMIN, ]
		
		mail = EmailMessage(
			subject=TITOLO_EMAIL_APERTURA.format(ticket=self.nome),
			body = testo,
			from_email = mittente, 
			to = destinatari, 
			bcc = bcc_list,
			reply_to = [EMAIL_ADMIN, ],
			)

		res = mail.send(fail_silently= True)		
#		res = send_mail(subject= TITOLO_EMAIL_APERTURA.format(ticket=self.nome), 
#					 message= testo, 
#					 from_email= mittente, 
#					 recipient_list= destinatari, 
#					 fail_silently= False
#		)
		return res
	
	def mail_chiusura(self):
#		testo = format_html(self.tipologia.email_chiusura, 
#					  self.persona, 
#					  datetime_format(self.data_chiusura), 
#					  self.utente_chiusura.last_name + " " + self.utente_chiusura.first_name, 
#					  self.soluzione
#					  )
		testo = formatta_testo_ticket(self.tipologia.email_chiusura, self)
		mittente = EMAIL_SENDER
		destinatari = [self.persona.email,]  
			
# 		res = send_mail(
# 			subject= TITOLO_EMAIL_CHIUSURA.format(ticket=self.nome), 
# 			message= testo, 
# 			from_email= mittente, 
# 			recipient_list= destinatari, 
# 			fail_silently= False,
# 		)

		mail = EmailMessage(
			subject =TITOLO_EMAIL_CHIUSURA.format(ticket=self.nome),
			body = testo,
			from_email = mittente, 
			to = destinatari, 
			reply_to = [EMAIL_ADMIN, ],
			)

		res = mail.send(fail_silently = True)
		
		return res		 
		
		
class Azione(Base_abstract):
	ticket = models.ForeignKey(Ticket, verbose_name='Ticket',related_name='azioni_rel', on_delete=models.CASCADE,)
	data_azione = models.DateTimeField(auto_now=True, )
	utente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Utente agente', null=True, blank=True,)
	nota = models.TextField('Descrizione azione', )
	interna = models.BooleanField('Annotazione interna', default=False)
	
	def __str__(self):
		text = "{cog} {dt:%d/%m/%Y}"
		ln = ""
		if not self.utente:
			ln = "-"
		else:
			ln = self.utente.last_name
		return text.format (cog = ln, dt = self.data_azione)
	
	def mail_azione(self, edp = False):
		
#		testo = format_html(self.ticket.tipologia.email_azione, 
#					  self.ticket.persona, 
#					  self.ticket, 
#					  self.utente.last_name + " " +self.utente.first_name, 
#					  self.nota
#					  )

		testo = formatta_testo_azione(self.ticket.tipologia.email_azione, self)
		mittente = EMAIL_SENDER
		destinatari = []
		if not edp:
			for ut in self.ticket.tipologia.gruppo.membri.all():
				destinatari.append(ut.email)
				
			#mittente = ticket.persona.email
		else:
			destinatari = [self.ticket.persona.email,]
		
		if len(destinatari) == 0:
			destinatari = [EMAIL_ADMIN, ]
		
# 		res = send_mail(subject= TITOLO_EMAIL_AZIONE.format(ticket=self.ticket.nome), 
# 					 message= testo, 
# 					 from_email= mittente, 
# 					 recipient_list= destinatari, 
# 					 fail_silently= False
# 		)
		
		mail=EmailMessage(
			subject = TITOLO_EMAIL_AZIONE.format(ticket=self.ticket.nome),
			body = testo,
			from_email=mittente, 
			to = destinatari, 
			reply_to = [EMAIL_ADMIN, ],
			)
		
		res = mail.send(fail_silently = True)
		
		return res
	
	class Meta:
		verbose_name = "Azione"
		verbose_name_plural = "Azioni"	
	
class Allegato(Base_abstract):
	nome = models.CharField("Descrizione dell'allegato",max_length=120,)
	file = models.FileField	('File Allegato', upload_to="allegati/%Y")
	ticket = models.ForeignKey(Ticket,on_delete=models.CASCADE, verbose_name='Ticket di riferimento', )
	
	def __str__(self):
		text = "{nom} ({tick})"
		return text.format(nom = self.nome, tick= self.ticket.nome)
	
	class Meta:
		verbose_name = "Allegato"
		verbose_name_plural = "Allegati"