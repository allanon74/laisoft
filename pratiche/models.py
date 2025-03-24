#import random
from django.db import models
from django.db.models import Sum
from dipendenti.models import Dipendente
import datetime
from django.core.mail import send_mail
from django.utils.html import format_html


# Create your models here.

STR_URL = 'https://d3leifers.gvcc.net/dms/r/dd44bb51-c2d5-59d8-aba3-cedc1047c97c/o2/'

EMAIL_HOST = "comune-laives-bz-it.mail.protection.outlook.com"
EMAIL_FROM = "urbanistica@comune.laives.bz.it"
EMAIL_PORT = 25
EMAIL_SUBJECT = "Assegnazione Pratica"

EMAIL_TEXT =  'Buon giorno. Ti è stata assegnata una nuova pratica da espletare.\r\n\r\n'
EMAIL_TEXT += 'Il documento {}, relativo alla pratica, lo trovi qui: {}\r\n\r\n'
EMAIL_TEXT += 'Il riepilogo delle pratiche lo trovi al link http://leifersdjango.leifers.gvcc.net/pratiche/lista/\r\n\r\n'
EMAIL_TEXT += 'Cordiali saluti.\r\n\r\n'
EMAIL_TEXT += 'Il dirigente \r\n\r\n'
EMAIL_TEXT += 'NOME DIRIGENTE'


def mail_delega(delega):
	return mail_completo(delega.assegnatario.email, delega.gruppo.mittente, delega.documento, delega.url_pratica(), delega.gruppo.titolo_email, delega.gruppo.email)

def mail_completo(destinatario, mittente, documento, url, titolo, testo):
# 	txt = 'Buon giorno. Ti è stata assegnata una nuova pratica da espletare.\r\n\r\n'
# 	txt += 'Il documento {}, relativo alla pratica, lo trovi qui: {}\r\n\r\n'
# 	txt += 'Il riepilogo delle pratiche lo trovi al link http://leifersdjango.leifers.gvcc.net/pratiche/lista/\r\n\r\n'
# 	txt += 'Cordiali saluti.\r\n\r\n'
# 	txt += 'Il dirigente \r\n\r\n'
# 	txt += 'Arch. Alessandra Montel'

  
#	Sendmail disabilitato per errori di login 
#
	res = send_mail(subject= titolo, 
				 message= format_html(testo, documento, url), 
				 from_email= mittente, 
				 recipient_list= (destinatario, ), 
				 fail_silently= False
	)

	#res = "NA"	
	return res

def mail_test(destinatario, mittente, documento, url, titolo, testo):

	res = send_mail(subject= titolo, 
				 message= format_html(testo, documento, url), 
				 from_email= mittente, 
				 recipient_list= (destinatario, ), 
				 fail_silently= False
	)

#	res = "NA"	
	return res	

class Base_abstract(models.Model):
	id = models.AutoField("Codice Identificativo", primary_key=True, )
	class Meta:
		abstract = True


class TipoPratica(Base_abstract):
	nome = models.CharField('Nome della pratica', max_length=30)
	note = models.TextField('Annotazioni', null=True, blank=True, )
	
	def __str__(self):
		return self.nome 
	
	class Meta:
		verbose_name = "Tipologia di pratica"
		verbose_name_plural = "Tipologie di pratiche"
		
class GruppoPratica(Base_abstract):
	nome = models.CharField('Nome del gruppo', max_length=30)
	responsabile = models.ForeignKey(Dipendente, on_delete=models.CASCADE, limit_choices_to = {'ruolo__responsabile' : True}, related_name='gruppo_responsabile',)
	gestori = models.ManyToManyField(Dipendente, related_name='gruppo_gestore',)
	titolo_email = models.CharField('Titolo della e-mail', max_length=120, default=EMAIL_SUBJECT,)
	mittente = models.CharField('Mittente della e-mail', max_length=120, default=EMAIL_FROM,)
	email = models.TextField('Testo della e-mail da inviare', default = EMAIL_TEXT,)
	delegato = models.ManyToManyField(
		Dipendente,
#		related_name = 'delegato',
		through='Dipendente_GruppoPratica',
		through_fields = ('gruppopratica','dipendente'),
		) 
	pratiche = models.ManyToManyField(
		TipoPratica, 
#		related_name = 'pratiche',
		)

	def __str__(self):
		return self.nome 
	
	class Meta:
		verbose_name = "Gruppo di gestione pratiche"
		verbose_name_plural = "Gruppi di gestione pratiche"
	
	
	
class Dipendente_GruppoPratica(Base_abstract):
	dipendente = models.ForeignKey(Dipendente, on_delete=models.CASCADE, )
	gruppopratica = models.ForeignKey(GruppoPratica, on_delete=models.CASCADE, )
	pratiche = models.ManyToManyField(
		TipoPratica, 
#		related_name = 'pratiche',
		)
	
	def __str__(self):
		text = "{dip} - {grp}"
		return text.format(dip=self.dipendente, grp=self.gruppopratica)
	
	class Meta:
		verbose_name = "Dipendente - Gruppo di gestione pratiche"
		verbose_name_plural = "Dipendenti - Gruppi di gestione pratiche"
	
 
	

class Delega(Base_abstract):
	documento = models.CharField('ID documento', max_length=10,)
	tipo_pratica = models.ForeignKey(TipoPratica, on_delete=models.CASCADE, verbose_name='Tipologia di pratica', default=1, )
	peso = models.IntegerField('Carico della pratica',)
	richiedente = models.CharField('Richiedente:', max_length=100, null=True, blank=True,)
	data_assegnazione = models.DateField('Data di assegnazione', auto_now_add=True, )
	pratica_collegata = models.CharField('ID pratica precedente collegata', max_length=10,null=True, blank=True, )
	gruppo = models.ForeignKey(GruppoPratica, on_delete=models.CASCADE, verbose_name='Gruppo gestione pratiche', default=1,)
	note = models.TextField('Annotazioni', null=True, blank=True, )
	assegnatario = models.ForeignKey(Dipendente, on_delete=models.CASCADE, verbose_name="Assegnatario della pratica",)
	completato = models.BooleanField("Pratica completata", default=False,)
	data_completamento = models.DateField('Data di completamento', null=True, blank=True,)
	system = models.BooleanField("sistema", default=False,)
	origine = models.CharField("Assegnazione", max_length= 50, null=True, blank=True, )
	
	def completa(self):
		self.data_completamento = datetime.datetime.now()
		self.completato = True
		self.update()
	
	def url_pratica(self):
		url = u"{base_url}{id_doc}"
		return url.format(base_url=STR_URL, id_doc=self.documento)
	
	def __str__(self):
		text= "{persona}:{ID}"
		return text.format(persona=self.assegnatario.cognome, ID=self.documento,)
	
	def save(self, *args, **kwargs):
		if not hasattr(self, 'assegnatario'):
			if not hasattr(self, 'pratica_collegata'):
#				deleg = self.gruppo.delegato.all()
				deleg = self.gruppo.delegato.filter(dipendente_gruppopratica__pratiche = self.tipo_pratica)
				q=deleg.filter(delega__completato=False).annotate(carico=Sum('delega__peso')).order_by('carico')
				self.assegnatario = q[0]
			else:
				dlg = Delega.objects.filter(documento__exact=self.pratica_collegata).order_by('-data_assegnazione')
				if len(dlg) == 0:
#					deleg = self.gruppo.delegato.all()
					deleg = self.gruppo.delegato.filter(dipendente_gruppopratica__pratiche = self.tipo_pratica)
					q=deleg.filter(delega__completato=False).annotate(carico=Sum('delega__peso')).order_by('carico')
					self.assegnatario = q[0]
				else:
					self.assegnatario = dlg[0].assegnatario
			txt = "Assegnazione Casuale - {data:%d/%m/%Y}"
			self.origine = txt.format(data = datetime.datetime.now())
			mail_delega(self)
		super(Delega, self).save(*args, **kwargs)
		 	
	class Meta:
		verbose_name = "Delega"
		verbose_name_plural = "Deleghe"