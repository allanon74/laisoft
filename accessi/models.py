from django.db import models
from django.conf import settings
from dipendenti.models import Dipendente, Dirigente, Ufficio

# Create your models here.

# Variabili 

DIRITTO_D3 = "D3"
TESTO = "TX"
GENERICO = "GE"
GRUPPO_O365 = "GO"
GEBEV = "GB"
ATTO = "AT"
TEMPLATE = "TE"
DESIGNAZIONE = "DE"
GRUPPO_WEB ="WW"
GRUPPO_SAMBA = "SA"
GRUPPO_GOFFICE2 = "G2"

gruppi_tipo =[
	(DIRITTO_D3, 'Diritto D3'),
	(TESTO, 'Testo'),
	(GENERICO, 'Generico'),
	(GRUPPO_O365, 'Gruppo Office365'),
	(GEBEV, 'Programa delibere'),
	(ATTO, "Atto"),
	(DESIGNAZIONE, "Designazione"),
	(GRUPPO_WEB, "Gruppo Web"),
	(GRUPPO_SAMBA, "Gruppo Samba"),
	(GRUPPO_GOFFICE2, "App Goffice2"),
	]


AMMINISTRATORE = "Amministratore"

# Funzioni

def StrDiritto(OnOff):
	txt = "."
	if OnOff:
		txt = "X"
	else:
		txt = " "
	return txt
	

# Modelli astratti
class Base_abstract(models.Model):
	id = models.AutoField("Codice Identificativo", primary_key=True, )
	
	class Meta:
		abstract = True

class Name_abstract(Base_abstract):
	nome = models.CharField("Nome del tipo di diritto", max_length = 20)
	
	def __str__(self):
		text = "{nm}"
		return text.format(nm=self.nome)
	
	class Meta:
		abstract = True
		
		
		
# Modelli 


class TipoGenerico(Name_abstract):
	nome_de = models.CharField("Nome del tipo in tedesco", max_length = 20, default="-")
	sigla = models.CharField("Sigla del diritto", max_length = 2, unique=True,)
	gruppo = models.CharField("Gruppo di tipologie", choices=gruppi_tipo, max_length=2)

	def __str__(self):
		text = "{nm} ({gr}-{si})"
		return text.format(nm=self.nome, gr=self.gruppo, si=self.sigla)
	
	class Meta:
		verbose_name = "Tipo Generico"
		verbose_name_plural = "Tipi Generici"
		
		
class AmbitiPassword(Name_abstract):
	nome = models.CharField("Nome dell'ambito password", max_length=30, )
	descrizione = models.TextField("Descrizione dettagliata", blank=True, null=True,)

	class Meta:
		verbose_name = "Ambito della password"
		verbose_name_plural = "Ambiti della password"


class TestoFisso(Name_abstract):
	nome = models.CharField("nome del testo fisso per atto", max_length=30, )
	testo_fisso_it = models.TextField("Testo fisso italiano", )
	testo_fisso_de = models.TextField("Testo fisso tedesco", )
	tipologia = models.ForeignKey(TipoGenerico, on_delete=models.CASCADE, verbose_name="Tipologia di testo fisso", limit_choices_to={'gruppo' : TESTO}) 
	
	def __str__(self):
		text = "{nm} ({si})"
		return text.format(nm=self.nome, si=self.tipologia)

	class Meta:
		verbose_name = "Testo fisso Atto"
		verbose_name_plural = "Testi fissi Atto"


class Capoverso(Base_abstract):
	ordine=models.IntegerField("ordine del capoverso",  )
	testofisso = models.ForeignKey(TestoFisso, verbose_name='testo Fisso di riferimento', on_delete=models.CASCADE)
	testo_it = models.TextField("Testo italiano", )
	testo_de = models.TextField("Testo tedesco", )
	
	def __str__(self):
		text = "{ntf} - {num}"
		return text.format(ntf=self.testofisso.nome, num=self.ordine)
	
	class Meta:
		verbose_name = "Capoverso testo fisso"
		verbose_name_plural = "Capoversi testo fisso"


class Share(Name_abstract):
	nome = models.CharField("nome dello share", max_length=30,)
	percorso = models.CharField("percorso di rete dello share", max_length=100, default='\\user\\document\\',)
	grupposamba = models.ForeignKey('GruppoSamba', 
								 on_delete=models.CASCADE, 
								 related_name="shares", 
								 verbose_name="Gruppo samba proprietario"
								 )	

	class Meta:
		verbose_name = "Share"
		verbose_name_plural = "Shares"


class Atto(Base_abstract):
	data = models.DateField("Data di decorrenza della validità dell'atto", )
	data_firma = models.DateField("Data della sottoscrizione", null=True, blank=True )
	tipo = models.ForeignKey(
		TipoGenerico, 
		on_delete=models.CASCADE,
		limit_choices_to={'gruppo' : ATTO},
		verbose_name= "Tipologia di Atto",
		)
	dipendente = models.ForeignKey(
								Dipendente, 
								on_delete = models.CASCADE,
								verbose_name = "Dipendente assegnatario",
								related_name = "atti"
								)
	amministratore = models.ForeignKey(
								Dipendente, 
								on_delete = models.CASCADE,
								verbose_name = "Amministratore di sistema",
								related_name = "atti_amm",
								limit_choices_to = {'ruolo__ammsistema' : True},
								)
	dirigente_alt = models.ForeignKey(
		Dirigente,
		on_delete = models.PROTECT,
		verbose_name = "Dirigente sostitutivo nell'ambito di trattamento",
		null=True, blank=True,
		help_text = "Lasciare in bianco per scegliere in automatico il dirigente corretto.",
		)
	def __str__(self):
		txt = "atto {tipo} {data:%d.%m.%Y} - {dip}"
		return txt.format(tipo=self.tipo, data=self.data, dip=self.dipendente)
	
	class Meta:
		verbose_name = "Atto"
		verbose_name_plural = "Atti"


class Autorizzazione(Base_abstract):
	data = models.DateField("Data di decorrenza della validità dell'autorizzazione", )
	data_firma = models.DateField("Data della sottoscrizione", null=True, blank=True )

	ufficio = models.ForeignKey(
								Ufficio, 
								on_delete = models.CASCADE,
								verbose_name = "Ufficio relativo",
								related_name = "autorizzazioni"
								)
	amministratore = models.ForeignKey(
								Dipendente, 
								on_delete = models.CASCADE,
								verbose_name = "Amministratore di sistema",
								related_name = "autorizzazione_amm",
								limit_choices_to = {'ruolo__ammsistema' : True},
								)
	dirigente_alt = models.ForeignKey(
		Dirigente,
		on_delete = models.PROTECT,
		verbose_name = "Dirigente sostitutivo nell'ambito di trattamento dell'autorizzazione",
		null=True, blank=True,
		help_text = "Lasciare in bianco per scegliere in automatico il dirigente corretto.",
		)
	
	testo = models.ForeignKey(TestoFisso, 
						   on_delete = models.CASCADE, 
						   verbose_name = 'Testo Fisso',
						   limit_choices_to = {'tipologia__nome' : "Autorizzazione"},
						   )
		
	def __str__(self):
		txt = "Autorizzazione Ufficio {ufficio} {data:%d.%m.%Y}"
		return txt.format(ufficio=self.ufficio, data=self.data)
	
	class Meta:
		verbose_name = "Autorizzazione"
		verbose_name_plural = "Autorizzazioni"

class Template(Base_abstract):
	data = models.DateField("Data di decorrenza della validità del template", )
	data_firma = models.DateField("Data della sottoscrizione", null=True, blank=True )
	nome = models.CharField("nome del template", max_length=20, )
	nome_int = models.CharField("nome del template in LDAP", max_length=20, null=True, blank=True, )

	autorizzazione = models.ForeignKey(
								Autorizzazione, 
								on_delete = models.CASCADE,
								verbose_name = "Autorizzazione gerarchica soprastante",
								related_name = "templates"
								)
	amministratore = models.ForeignKey(
								Dipendente, 
								on_delete = models.CASCADE,
								verbose_name = "Amministratore di sistema",
								related_name = "template_amm",
								limit_choices_to = {'ruolo__ammsistema' : True},
								)
	dirigente_alt = models.ForeignKey(
		Dirigente,
		on_delete = models.PROTECT,
		verbose_name = "Dirigente sostitutivo nell'ambito di trattamento dell'autorizzazione",
		null=True, blank=True,
		help_text = "Lasciare in bianco per scegliere in automatico il dirigente corretto.",
		)
	
	testo = models.ForeignKey(TestoFisso, 
						   on_delete = models.CASCADE, 
						   verbose_name = 'Testo Fisso',
						   limit_choices_to = {'tipologia__nome' : "Template"},
						   )
		
	def __str__(self):
		txt = "Template diritti {nome} {data:%d.%m.%Y}"
		return txt.format(nome=self.nome, data=self.data)
	
	class Meta:
		verbose_name = "Template"
		verbose_name_plural = "Templates"

	


class Password(Base_abstract):
	password = models.CharField("Password temporanea", max_length=24, )
	data_attribuzione =models.DateField("Data dell'attribuzione", )
	ambiti = models.ManyToManyField(
		AmbitiPassword, 
		verbose_name="Ambiti della password", 
		)
	testo = models.ForeignKey(TestoFisso, 
						   on_delete = models.CASCADE, 
						   verbose_name = 'Testo Fisso',
						   limit_choices_to = {'tipologia__nome' : "Password"},
						   )
	atto = models.OneToOneField(
								Atto, 
								on_delete = models.CASCADE,
								verbose_name = "Atto di assegnazione",
								)
	
	def __str__(self):
		text = "password {dp} - {dt:%d.%m.%Y}"
		return text.format(dp=self.atto.dipendente, dt=self.data_attribuzione)

	class Meta:
		verbose_name = "Attribuzione password"
		verbose_name_plural = "Attribuzioni password"


class Designazione(Base_abstract):
	data_designazione = models.DateField("Data della designazione", )
	testo = models.ForeignKey(TestoFisso, 
						   on_delete = models.CASCADE, 
						   verbose_name = 'Testo Fisso',
						   limit_choices_to = {'tipologia__nome' : "Designazione"},
						   )
	atto = models.OneToOneField(
								Atto, 
								on_delete = models.CASCADE,
								verbose_name = "Atto di designazione",			
								)	

	def __str__(self):
		text = "Designazione {dp} - {dt:%d.%m.%Y}"
		return text.format(dp=self.atto.dipendente, dt=self.data_designazione)

	class Meta:
		verbose_name = "Designazione autorizzato"
		verbose_name_plural = "Designazioni autorizzati"



# Classi Diritto ed ereditate

class Diritto(Base_abstract):
	nome = models.CharField("Nome breve del diritto", max_length = 80, )
	nome_it = models.CharField("Nome del diritto in italiano", max_length = 150, null=True, blank=True,)
	nome_de = models.CharField("Nome del diritto in tedesco", max_length = 150, null=True, blank=True,)
	descrizione = models.TextField("Descrizione del diritto in italiano", null=True, blank=True,)
	descrizione_de = models.TextField("Descrizione del diritto in tedesco", null=True, blank=True,)
	attivo = models.BooleanField("diritto attivo", default=True,)

	def __str__(self):
		text = "{nome}"
		return text.format(nome=self.nome)
	
	class Meta:
		verbose_name = "Diritto"
		verbose_name_plural = "Diritti"		
		abstract = True
	

class GruppoSamba(Diritto):
	atti = models.ManyToManyField(
								"Atto", 
								through = "Atto_GruppoSamba",
								related_name = "gruppi_samba",
								verbose_name = "Atto di Assegnazione",
								)
	autorizzazioni = models.ManyToManyField(
								"Autorizzazione", 
								through = "Autorizzazione_GruppoSamba",
								related_name = "gruppi_samba",
								verbose_name = "Autorizzazione d'ufficio",
								)
	templates = models.ManyToManyField(
								"Template", 
								through = "Template_GruppoSamba",
								related_name = "gruppi_samba",
								verbose_name = "Template precostruito",
								)
	tipologia = models.ForeignKey(
		TipoGenerico, 
		on_delete=models.CASCADE, 
		verbose_name="Tipologia di diritto Samba", 
		limit_choices_to={'gruppo' : GRUPPO_SAMBA},
		null=True, blank=True, 
		)
	 
	class Meta:
		verbose_name = "Gruppo Samba"
		verbose_name_plural = "Gruppi Samba"
		ordering = ["tipologia", "nome",]


class SGVCanale(Diritto):
	atti = models.ManyToManyField(
								"Atto", 
								through = "Atto_SGVCanale",
								related_name = "sgvcanale",
								verbose_name = "Atto di Assegnazione",
								)
	autorizzazioni = models.ManyToManyField(
								"Autorizzazione", 
								through = "Autorizzazione_SGVCanale",
								related_name = "sgvcanale",
								verbose_name = "Autorizzazione d'ufficio",
								)
	templates = models.ManyToManyField(
								"Template", 
								through = "Template_SGVCanale",
								related_name = "sgvcanale",
								verbose_name = "Template precostruito",
								)	
	class Meta:
		verbose_name = "Lista di distribuzione SGV"
		verbose_name_plural = "Liste di Distribuzione SGV"
		ordering = ["nome"]		


class GOffice(Diritto):
	atti = models.ManyToManyField(
								"Atto", 
								through = "Atto_GOffice",
								related_name = "goffice",
								verbose_name = "Atto di Assegnazione",
								)
	autorizzazioni = models.ManyToManyField(
								"Autorizzazione", 
								through = "Autorizzazione_GOffice",
								related_name = "goffice",
								verbose_name = "Autorizzazione d'ufficio",
								)
	templates = models.ManyToManyField(
								"Template", 
								through = "Template_GOffice",
								related_name = "goffice",
								verbose_name = "Template precostruito",
								)

	def __str__(self):
		text = "{nome_it} ({nome})"
		return text.format(nome=self.nome, nome_it = self.nome_it)
 
	class Meta:
		verbose_name = "Diritto GOffice"
		verbose_name_plural = "Diritti GOffice"
		ordering = ["nome"]


class D3Gruppo(Diritto):
	# nome = models.CharField("Nome del diritto in italiano", max_length = 70, )
	# nome_de = models.CharField("Nome del diritto in tedesco", max_length = 70, null=True, blank=True,)
	atti = models.ManyToManyField(
								"Atto", 
								through = "Atto_D3Gruppo",
								related_name = "d3gruppi",
								verbose_name = "Atto di Assegnazione",
								)
	autorizzazioni = models.ManyToManyField(
								"Autorizzazione", 
								through = "Autorizzazione_D3Gruppo",
								related_name = "d3gruppi",
								verbose_name = "Autorizzazione d'ufficio",
								)
	templates = models.ManyToManyField(
								"Template", 
								through = "Template_D3Gruppo",
								related_name = "d3gruppi",
								verbose_name = "Template precostruito",
								)

	def __str__(self):
		text = "{cod} - {nome}"
		return text.format(nome=self.nome_it, cod=self.nome)

	class Meta:
		verbose_name = "Diritto Gruppo D3"
		verbose_name_plural = "Diritti Gruppi D3"	
		ordering = ["nome"]


class D3Diritto(Diritto):
	atti = models.ManyToManyField(
								"Atto", 
								through = "Atto_D3Diritto",
								related_name = "d3diritti",
								verbose_name = "Atto di Assegnazione",
								)
	autorizzazioni = models.ManyToManyField(
								"Autorizzazione", 
								through = "Autorizzazione_D3Diritto",
								related_name = "d3diritti",
								verbose_name = "Autorizzazione d'ufficio",
								)
	templates = models.ManyToManyField(
								"Template", 
								through = "Template_D3Diritto",
								related_name = "d3diritti",
								verbose_name = "Template precostruito",
								)
	tipologia = models.ForeignKey(TipoGenerico, 
							   on_delete=models.CASCADE, 
							   verbose_name="Tipologia di Diritto D3", 
							   limit_choices_to={'gruppo' : DIRITTO_D3}, 
							   ) 

	def __str__(self):
		text = "{tipo} - {nome}"
		return text.format(nome=self.nome, tipo=self.tipologia)
	
	class Meta:
		verbose_name = "Diritto D3"
		verbose_name_plural = "Diritti D3"
		ordering = ["tipologia", "nome"]


class Generico(Diritto):
	atti = models.ManyToManyField(
								"Atto", 
								through = "Atto_Generico",
								related_name = "generici",
								verbose_name = "Atto di Assegnazione",
								)
	autorizzazioni = models.ManyToManyField(
								"Autorizzazione", 
								through = "Autorizzazione_Generico",
								related_name = "generici",
								verbose_name = "Autorizzazione d'ufficio",
								)
	templates = models.ManyToManyField(
								"Template", 
								through = "Template_Generico",
								related_name = "generici",
								verbose_name = "Template precostruito",
								)

	class Meta:
		verbose_name = "Diritto Generico"
		verbose_name_plural = "Diritti Generici"
		ordering = ["nome"]


class DirittoRete(Diritto):
	atti = models.ManyToManyField(
								"Atto", 
								through = "Atto_DirittoRete",
								related_name = "diritti_rete",
								verbose_name = "Atto di Assegnazione",
								)
	autorizzazioni = models.ManyToManyField(
								"Autorizzazione", 
								through = "Autorizzazione_DirittoRete",
								related_name = "diritti_rete",
								verbose_name = "Autorizzazione d'ufficio",
								)
	templates = models.ManyToManyField(
								"Template", 
								through = "Template_DirittoRete",
								related_name = "diritti_rete",
								verbose_name = "Template precostruito",
								)
	class Meta:
		verbose_name = "Diritto di Rete"
		verbose_name_plural = "Diritti di Rete"
		ordering = ["nome"]


class O365Gruppo(Diritto):
	atti = models.ManyToManyField(
								"Atto", 
								through = "Atto_O365Gruppo",
								related_name = "o365gruppi",
								verbose_name = "Atto di Assegnazione",
								)
	autorizzazioni = models.ManyToManyField(
								"Autorizzazione", 
								through = "Autorizzazione_O365Gruppo",
								related_name = "o365gruppi",
								verbose_name = "Autorizzazione d'ufficio",
								)
	templates = models.ManyToManyField(
								"Template", 
								through = "Template_O365Gruppo",
								related_name = "o365gruppi",
								verbose_name = "Template precostruito",
								)
	tipologia = models.ForeignKey(TipoGenerico, on_delete=models.CASCADE, verbose_name="Tipologia di gruppo Office365", limit_choices_to={'gruppo' : GRUPPO_O365},) 

	def __str__(self):
		text = "{tipo} - {nome}"
		return text.format(nome=self.nome, tipo=self.tipologia)

	class Meta:
		verbose_name = "Gruppo Office365"
		verbose_name_plural = "Gruppi Office365"
		ordering = ["tipologia" ,"nome"]


class NextCloud(Diritto):
	atti = models.ManyToManyField(
								"Atto", 
								through = "Atto_NextCloud",
								related_name = "nextcloud",
								verbose_name = "Atto di Assegnazione",
								)
	autorizzazioni = models.ManyToManyField(
								"Autorizzazione", 
								through = "Autorizzazione_NextCloud",
								related_name = "nextcloud",
								verbose_name = "Autorizzazione d'ufficio",
								)
	templates = models.ManyToManyField(
								"Template", 
								through = "Template_NextCloud",
								related_name = "nextcloud",
								verbose_name = "Template precostruito",
								)

	class Meta:
		verbose_name = "Gruppo Nextcloud"
		verbose_name_plural = "Gruppi Nextcloud"
		ordering = ["nome"]
	
	
class Porta(Diritto):
	atti = models.ManyToManyField(
								"Atto", 
								through = "Atto_Porta",
								#on_delete = models.CASCADE, 
								related_name = "porte",
								verbose_name = "Atto di Assegnazione",
								)
	autorizzazioni = models.ManyToManyField(
								"Autorizzazione", 
								through = "Autorizzazione_Porta",
								related_name = "porte",
								verbose_name = "Autorizzazione d'ufficio",
								)
	templates = models.ManyToManyField(
								"Template", 
								through = "Template_Porta",
								related_name = "porte",
								verbose_name = "Template precostruito",
								)
	num_stanza = models.IntegerField('Numero Stanza', null=True, blank=True,)
	transponder = models.IntegerField('Codice Transponder', null=True, blank=True,)

	def __str__(self):
		text = "{stanza}{nome} ({trans})"
		txt_stanza = ""
		if self.num_stanza:
			txt = "Stanza {num:03d} - "
			txt_stanza = txt.format(num=self.num_stanza)
		return text.format(nome=self.nome, stanza = txt_stanza, trans=self.transponder)
	
	class Meta:
		verbose_name = "Porta"
		verbose_name_plural = "Porte"
		ordering = ["transponder", "nome"]
		

class WebApp(Diritto):
	atti = models.ManyToManyField(
								"Atto", 
								through = "Atto_WebApp",
								#on_delete = models.CASCADE, 
								related_name = "django",
								verbose_name = "Atto di Assegnazione",
								)
	autorizzazioni = models.ManyToManyField(
								"Autorizzazione", 
								through = "Autorizzazione_WebApp",
								related_name = "django",
								verbose_name = "Autorizzazione d'ufficio",
								)
	templates = models.ManyToManyField(
								"Template", 
								through = "Template_WebApp",
								related_name = "django",
								verbose_name = "Template precostruito",
								) 

	class Meta:
		verbose_name = "Diritto WebApp Django"
		verbose_name_plural = "Diritti WebApp Django"
		ordering = ["nome"]


class GebevDiritto(Diritto):
	atti = models.ManyToManyField(
								"Atto", 
								through = "Atto_GebevDiritto",
								#on_delete = models.CASCADE, 
								related_name = "gebev_diritti",
								verbose_name = "Atto di Assegnazione",
								)
	autorizzazioni = models.ManyToManyField(
								"Autorizzazione", 
								through = "Autorizzazione_GebevDiritto",
								related_name = "gebev_diritti",
								verbose_name = "Autorizzazione d'ufficio",
								)
	templates = models.ManyToManyField(
								"Template", 
								through = "Template_GebevDiritto",
								related_name = "gebev_diritti",
								verbose_name = "Template precostruito",
								)
	tipologia = models.ForeignKey(
		TipoGenerico, 
		on_delete=models.CASCADE, 
		verbose_name="Tipologia di diritto programma delibere", 
		limit_choices_to={'gruppo' : GEBEV},
		) 


	def __str__(self):
		text = "{tipo} - {nome}"
		return text.format(nome=self.nome, tipo=self.tipologia)

	class Meta:
		verbose_name = "Diritto Programma Delibere"
		verbose_name_plural = "Diritti Programma Delibere"
		ordering = ["tipologia", "nome"]

class GebevRipartizione(Diritto):
	nome = models.CharField("Nome del diritto in italiano", max_length = 80, )
	nome_de = models.CharField("Nome del diritto in tedesco", max_length = 80, null=True, blank=True,)
	atti = models.ManyToManyField(
								"Atto", 
								through = "Atto_GebevRipartizione",
								#on_delete = models.CASCADE, 
								related_name = "gebev_ripartizioni",
								verbose_name = "Atto di Assegnazione",
								)
	autorizzazioni = models.ManyToManyField(
								"Autorizzazione", 
								through = "Autorizzazione_GebevRipartizione",
								#on_delete = models.CASCADE, 
								related_name = "gebev_ripartizioni",
								verbose_name = "Autorizzazione d'ufficio",
								)
	templates = models.ManyToManyField(
								"Template", 
								through = "Template_GebevRipartizione",
								related_name = "gebev_ripartizioni",
								verbose_name = "Template precostruito",
								)

	class Meta:
		verbose_name = "Ripartizione programa Delibere"
		verbose_name_plural = "Ripartizioni programa Delibere"
		ordering = ["nome"]
		
		
class Web(Diritto):
	atti = models.ManyToManyField(
								"Atto", 
								through = "Atto_Web",
								#on_delete = models.CASCADE, 
								related_name = "web",
								verbose_name = "Atto di Assegnazione",
								)
	autorizzazioni = models.ManyToManyField(
								"Autorizzazione", 
								through = "Autorizzazione_Web",
								#on_delete = models.CASCADE, 
								related_name = "web",
								verbose_name = "Autorizzazione d'ufficio",
								)
	templates = models.ManyToManyField(
								"Template", 
								through = "Template_Web",
								related_name = "web",
								verbose_name = "Template precostruito",
								)

	class Meta:
		verbose_name = "Diritto Pagina Web"
		verbose_name_plural = "Diritti Pagine Web"
		ordering = ["nome"]


class GOffice2(Diritto):
	atti = models.ManyToManyField(
								"Atto", 
								through = "Atto_GOffice2",
								#on_delete = models.CASCADE, 
								related_name = "goffice2",
								verbose_name = "Atto di Assegnazione",
								)
	autorizzazioni = models.ManyToManyField(
								"Autorizzazione", 
								through = "Autorizzazione_GOffice2",
								#on_delete = models.CASCADE, 
								related_name = "goffice2",
								verbose_name = "Autorizzazione d'ufficio",
								)
	templates = models.ManyToManyField(
								"Template", 
								through = "Template_GOffice2",
								related_name = "wegoffice2b",
								verbose_name = "Template precostruito",
								)

	class Meta:
		verbose_name = "Modulo GOffice2"
		verbose_name_plural = "Moduli GOffice2"
		ordering = ["nome"]

			
# Classi Through
		
class Entita_Diritto(Base_abstract):
#	atto = models.ForeignKey(Atto, on_delete=models.CASCADE, verbose_name = "Atti",)
#	diritto = models.ForeignKey(Diritto, on_delete=models.CASCADE, verbose_name = "Diritti",)
	data_inserimento = models.DateTimeField("Data di inserimento", auto_now_add=True, )
	data_modifica = models.DateTimeField("Data ultima modifica", auto_now=True, )
	data_disattivazione = models.DateTimeField("Data di disattivazione", null=True, blank=True,)
	utente_inserimento = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE, verbose_name='utente di attribuzione diritto',)
	utente_modifica = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE, verbose_name='utente di modifica diritto',)
	utente_disattivazione = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE, verbose_name='utente di disattivazione diritto', null=True, blank=True, )
	diritto_attivato = models.BooleanField("Diritto assegnato", default=False, )
	utente_admin = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE, verbose_name='Utente amministratore abilitante', null=True, blank=True,)
		
	
	class Meta:
		verbose_name = "Entità - Diritto"
		verbose_name_plural = "Entità - Diritti"
		abstract = True
		#ordering = ["diritto"]

class Atto_Diritto(Entita_Diritto):
	atto = models.ForeignKey(Atto, on_delete=models.CASCADE, verbose_name = "Atti",)
	
	def __str__(self):
		text = "{dip} - {diritto}"
		return text.format(dip=self.atto.dipendente, diritto=self.diritto)

	class Meta:
		verbose_name = "Dipendente - Diritto"
		verbose_name_plural = "Dipendenti - Diritti"
		abstract = True
		#ordering = ["diritto"]

class Autorizzazione_Diritto(Entita_Diritto):
	autorizzazione = models.ForeignKey(Autorizzazione, on_delete=models.CASCADE, verbose_name = "Autorizzazioni",)
	
	def __str__(self):
		text = "{uff} - {diritto}"
		return text.format(uff=self.autorizzazione.ufficio, diritto=self.diritto)

	class Meta:
		verbose_name = "Autorizzazione - Diritto"
		verbose_name_plural = "Autorizzazioni - Diritti"
		abstract = True
		#ordering = ["diritto"]


class Template_Diritto(Entita_Diritto):
	template = models.ForeignKey(Template, on_delete=models.CASCADE, verbose_name = "Templates",)
	
	def __str__(self):
		text = "{uff} - {diritto}"
		return text.format(uff=self.template.nome, diritto=self.diritto)

	class Meta:
		verbose_name = "Template - Diritto"
		verbose_name_plural = "Templates - Diritti"
		abstract = True
		#ordering = ["diritto"]

# GruppoSamba

class Entita_GruppoSamba(Base_abstract):
	diritto = models.ForeignKey(GruppoSamba, on_delete=models.CASCADE, verbose_name = "Gruppo Samba",limit_choices_to={'attivo' : True})
	
	class Meta:
		ordering = ["diritto"]
		abstract = True

class Atto_GruppoSamba(Atto_Diritto, Entita_GruppoSamba):
	
	class Meta:
		verbose_name = "Dipendente - Gruppo Samba"	
		verbose_name_plural = "Dipendenti - Gruppi Samba"
		
class Autorizzazione_GruppoSamba(Autorizzazione_Diritto, Entita_GruppoSamba):
	
	class Meta:
		verbose_name = "Ufficio - Gruppo Samba"	
		verbose_name_plural = "Uffici - Gruppi Samba"

class Template_GruppoSamba(Template_Diritto, Entita_GruppoSamba):
	
	class Meta:
		verbose_name = "Template - Gruppo Samba"	
		verbose_name_plural = "Templates - Gruppi Samba"

# SGVCanale

class Entita_SGVCanale(Base_abstract):
	diritto = models.ForeignKey(SGVCanale, on_delete=models.CASCADE, verbose_name = "Lista Distribuzione SGV",limit_choices_to={'attivo' : True})
	
	class Meta:
		abstract = True
		ordering = ["diritto"]


class Atto_SGVCanale(Atto_Diritto, Entita_SGVCanale):
	
	class Meta:
		verbose_name = "Dipendente - Lista Distribuzione SGV"	
		verbose_name_plural = "Dipendenti - Liste Distribuzione SGV"

		
class Autorizzazione_SGVCanale(Autorizzazione_Diritto, Entita_SGVCanale):

	class Meta:
		verbose_name = "Ufficio - Lista Distribuzione SGV"	
		verbose_name_plural = "Uffici - Liste Distribuzione SGV"


class Template_SGVCanale(Template_Diritto, Entita_SGVCanale):
	
	class Meta:
		verbose_name = "Template - Lista Distribuzione SGV"	
		verbose_name_plural = "Templates - Liste Distribuzione SGV"

# GOffice
		
class Entita_GOffice(Base_abstract):
	diritto = models.ForeignKey(GOffice, on_delete=models.CASCADE, verbose_name = "Diritto GOffice",limit_choices_to={'attivo' : True})
	
	class Meta:
		abstract = True
		ordering = ["diritto"]


class Atto_GOffice(Atto_Diritto, Entita_GOffice):
	
	class Meta:
		verbose_name = "Dipendente - Diritto GOffice"	
		verbose_name_plural = "Dipendenti - Diritti GOffice"


class Autorizzazione_GOffice(Autorizzazione_Diritto, Entita_GOffice):
	
	class Meta:
		verbose_name = "Ufficio - Diritto GOffice"	
		verbose_name_plural = "Uffici - Diritti GOffice"
		
		
class Template_GOffice(Template_Diritto, Entita_GOffice):
	
	class Meta:
		verbose_name = "Template - Diritto GOffice"	
		verbose_name_plural = "Templates - Diritti GOffice"

# D3Gruppo

class Entita_D3Gruppo(Base_abstract):
	diritto = models.ForeignKey(D3Gruppo, on_delete=models.CASCADE, verbose_name = "Diritto di Gruppo D3",limit_choices_to={'attivo' : True})
	lettura = models.BooleanField("Lettura documenti", default=True, )
	scrittura = models.BooleanField("Modifica documenti", default=True, )
	lettura_r = models.BooleanField("Lettura documenti riservati", default=False, )
	scrittura_r = models.BooleanField("Modifica documenti riservati", default=False, )
	posta = models.BooleanField("Accesso casella postale", default=True, )
	
	class Meta:
		abstract = True
		ordering = ["diritto"]
		

class Atto_D3Gruppo(Atto_Diritto, Entita_D3Gruppo):

	def __str__(self):
		text = "{dip} - {diritto}: {diritti}"
		t_dir=""
		if self.lettura:
			t_dir += "(R)"
		if self.scrittura:
			t_dir +="(S)"
		if self.lettura_r:
			t_dir += "(Rr)"
		if self.scrittura_r:
			t_dir +="(Sr)"
		if self.posta:
			t_dir += "(P)"
		return text.format(dip=self.atto.dipendente, diritto=self.diritto, diritti=t_dir)
	
	class Meta:
		verbose_name = "Dipendente - Diritto Gruppo D3"	
		verbose_name_plural = "Dipendenti - Diritti Gruppi D3"


class Autorizzazione_D3Gruppo(Autorizzazione_Diritto, Entita_D3Gruppo):

	def __str__(self):
		text = "{uff} - {diritto}: {diritti}"
		t_dir=""
		if self.lettura:
			t_dir += "(R)"
		if self.scrittura:
			t_dir +="(S)"
		if self.lettura_r:
			t_dir += "(Rr)"
		if self.scrittura_r:
			t_dir +="(Sr)"
		if self.posta:
			t_dir += "(P)"
		return text.format(uff=self.autorizzazione.ufficio, diritto=self.diritto, diritti=t_dir)
	
	class Meta:
		verbose_name = "Ufficio - Diritto Gruppo D3"	
		verbose_name_plural = "Uffici - Diritti Gruppi D3"


class Template_D3Gruppo(Template_Diritto, Entita_D3Gruppo):

	def __str__(self):
		text = "{tpl} - {diritto}: {diritti}"
		t_dir=""
		if self.lettura:
			t_dir += "(R)"
		if self.scrittura:
			t_dir +="(S)"
		if self.lettura_r:
			t_dir += "(Rr)"
		if self.scrittura_r:
			t_dir +="(Sr)"
		if self.posta:
			t_dir += "(P)"
		return text.format(tpl=self.template.nome, diritto=self.diritto, diritti=t_dir)
	
	class Meta:
		verbose_name = "Template - Diritto Gruppo D3"	
		verbose_name_plural = "Templates - Diritti Gruppi D3"

# D3Diritto		
		
class Entita_D3Diritto(Base_abstract):
	diritto = models.ForeignKey(D3Diritto, on_delete=models.CASCADE, verbose_name = "Diritto D3",limit_choices_to={'attivo' : True})

	class Meta:
		abstract = True
		ordering = ["diritto"]
		
		
class Atto_D3Diritto(Atto_Diritto, Entita_D3Diritto):

	class Meta:
		verbose_name = "Dipendente - Diritto D3"	
		verbose_name_plural = "Dipendenti - Diritti D3"


class Autorizzazione_D3Diritto(Autorizzazione_Diritto, Entita_D3Diritto):

	class Meta:
		verbose_name = "Ufficio - Diritto D3"	
		verbose_name_plural = "Uffici - Diritti D3"


class Template_D3Diritto(Template_Diritto, Entita_D3Diritto):

	class Meta:
		verbose_name = "Template - Diritto D3"	
		verbose_name_plural = "Templates - Diritti D3"

# Generico

class Entita_Generico(Base_abstract):
	diritto = models.ForeignKey(Generico, on_delete=models.CASCADE, verbose_name = "Sottosistema Ascot",limit_choices_to={'attivo' : True})
	tipo = models.ForeignKey(TipoGenerico, on_delete=models.CASCADE, verbose_name = "Tipologia di diritto", limit_choices_to={'gruppo' : GENERICO})

	class Meta:
		abstract = True
		ordering = ["diritto"]


class Atto_Generico(Atto_Diritto, Entita_Generico):

	def __str__(self):
		text = "{dip} - {diritto}: {tipo}"
		return text.format(dip=self.atto.dipendente, diritto=self.diritto, tipo=self.tipo)
	
	class Meta:
		verbose_name = "Dipendente - Diritto Ascot"	
		verbose_name_plural = "Dipendenti - Diritti Ascot"

class Autorizzazione_Generico(Autorizzazione_Diritto, Entita_Generico):

	def __str__(self):
		text = "{uff} - {diritto}: {tipo}"
		return text.format(uff=self.autorizzazione.ufficio, diritto=self.diritto, tipo=self.tipo)
	
	class Meta:
		verbose_name = "Ufficio - Diritto Ascot"	
		verbose_name_plural = "Ufficio - Diritti Ascot"


class Template_Generico(Template_Diritto, Entita_Generico):

	def __str__(self):
		text = "{tpl} - {diritto}: {tipo}"
		return text.format(tpl=self.template.nome, diritto=self.diritto, tipo=self.tipo)
	
	class Meta:
		verbose_name = "Template - Diritto Ascot"	
		verbose_name_plural = "Templates - Diritti Ascot"

# DirittoRete

class Entita_DirittoRete(Base_abstract):
	diritto = models.ForeignKey(DirittoRete, on_delete=models.CASCADE, verbose_name = "Diritto di Rete",limit_choices_to={'attivo' : True})
	annotazioni = models.CharField("Note aggiuntive", max_length=50, null=True, blank=True, )

	class Meta:
		abstract = True
		ordering = ["diritto"]


class Atto_DirittoRete(Atto_Diritto, Entita_DirittoRete):
	
	class Meta:
		verbose_name = "Dipendente - Diritto di Rete"	
		verbose_name_plural = "Dipendenti - Diritti di Rete"


class Autorizzazione_DirittoRete(Autorizzazione_Diritto, Entita_DirittoRete):
	
	class Meta:
		verbose_name = "Ufficio - Diritto di Rete"	
		verbose_name_plural = "Uffici - Diritti di Rete"


class Template_DirittoRete(Template_Diritto, Entita_DirittoRete):
	
	class Meta:
		verbose_name = "Template - Diritto di Rete"	
		verbose_name_plural = "Templates - Diritti di Rete"

#O365Gruppo

class Entita_O365Gruppo(Base_abstract):
	diritto = models.ForeignKey(O365Gruppo, on_delete=models.CASCADE, verbose_name = "Gruppo Office 365",limit_choices_to={'attivo' : True})

	class Meta:
		abstract = True
		ordering = ["diritto"]


class Atto_O365Gruppo(Atto_Diritto, Entita_O365Gruppo):

	class Meta:
		verbose_name = "Dipendente - Gruppo Office 365"	
		verbose_name_plural = "Dipendenti - Gruppi Office 365"


class Autorizzazione_O365Gruppo(Autorizzazione_Diritto, Entita_O365Gruppo):

	class Meta:
		verbose_name = "Ufficio - Gruppo Office 365"	
		verbose_name_plural = "Uffici - Gruppi Office 365"

class Template_O365Gruppo(Template_Diritto, Entita_O365Gruppo):

	class Meta:
		verbose_name = "Template - Gruppo Office 365"	
		verbose_name_plural = "Templates - Gruppi Office 365"


# NextCloud

class Entita_NextCloud(Base_abstract):
	diritto = models.ForeignKey(NextCloud, on_delete=models.CASCADE, verbose_name = "Gruppo NextCloud",limit_choices_to={'attivo' : True})
	tipo = models.ForeignKey(TipoGenerico, on_delete=models.CASCADE, verbose_name = "Tipologia di diritto", limit_choices_to={'gruppo' : GENERICO})
	
	class Meta:
		abstract = True
		ordering = ["diritto"]


class Atto_NextCloud(Atto_Diritto, Entita_NextCloud):

	def __str__(self):
		text = "{dip} - {diritto}: {tipo}"
		return text.format(dip=self.atto.dipendente, diritto=self.diritto, tipo=self.tipo)
	
	class Meta:
		verbose_name = "Dipendente - Gruppo NextCloud"	
		verbose_name_plural = "Dipendenti - Gruppi NextCloud"


class Autorizzazione_NextCloud(Autorizzazione_Diritto, Entita_NextCloud):

	def __str__(self):
		text = "{uff} - {diritto}: {tipo}"
		return text.format(uff=self.autorizzazione.ufficio, diritto=self.diritto, tipo=self.tipo)
	
	class Meta:
		verbose_name = "Ufficio - Gruppo NextCloud"	
		verbose_name_plural = "Uffici - Gruppi NextCloud"


class Template_NextCloud(Template_Diritto, Entita_NextCloud):

	def __str__(self):
		text = "{tpl} - {diritto}: {tipo}"
		return text.format(tpl=self.template.nome, diritto=self.diritto, tipo=self.tipo)
	
	class Meta:
		verbose_name = "Template - Gruppo NextCloud"	
		verbose_name_plural = "Templates - Gruppi NextCloud"


# Porta

class Entita_Porta(Base_abstract):
	diritto = models.ForeignKey(Porta, on_delete=models.CASCADE, verbose_name = "Porta",limit_choices_to={'attivo' : True})

	class Meta:
		abstract = True
		ordering = ["diritto"]


class Atto_Porta(Atto_Diritto, Entita_Porta):

	class Meta:
		verbose_name = "Dipendente - Porta"	
		verbose_name_plural = "Dipendenti - Porte"


class Autorizzazione_Porta(Autorizzazione_Diritto, Entita_Porta):

	class Meta:
		verbose_name = "Ufficio - Porta"	
		verbose_name_plural = "Uffici - Porte"


class Template_Porta(Template_Diritto, Entita_Porta):

	class Meta:
		verbose_name = "Template - Porta"	
		verbose_name_plural = "Templates - Porte"


# WebApp

class Entita_WebApp(Base_abstract):
	diritto = models.ForeignKey(WebApp, on_delete=models.CASCADE, verbose_name = "Diritto WebApp Django",limit_choices_to={'attivo' : True})

	class Meta:
		abstract = True
		ordering = ["diritto"]


class Atto_WebApp(Atto_Diritto, Entita_WebApp):

	class Meta:
		verbose_name = "Dipendente - Diritto WebApp Django"	
		verbose_name_plural = "Dipendenti - Diritti WebApp Django"


class Autorizzazione_WebApp(Autorizzazione_Diritto, Entita_WebApp):

	class Meta:
		verbose_name = "Ufficio - Diritto WebApp Django"	
		verbose_name_plural = "Uffici - Diritti WebApp Django"


class Template_WebApp(Template_Diritto, Entita_WebApp):

	class Meta:
		verbose_name = "Template - Diritto WebApp Django"	
		verbose_name_plural = "Templates - Diritti WebApp Django"
  

# GebevDiritto

class Entita_GebevDiritto(Base_abstract):
	diritto = models.ForeignKey(GebevDiritto, on_delete=models.CASCADE, verbose_name = "Diritto Generale Programa delibere",limit_choices_to={'attivo' : True})

	class Meta:
		abstract = True
		ordering = ["diritto"]


class Atto_GebevDiritto(Atto_Diritto, Entita_GebevDiritto):

	class Meta:
		verbose_name = "Dipendente - Diritto Generale Delibere"	
		verbose_name_plural = "Dipendenti - Diritti Generali Delibere"


class Autorizzazione_GebevDiritto(Autorizzazione_Diritto, Entita_GebevDiritto):

	class Meta:
		verbose_name = "Ufficio - Diritto Generale Delibere"	
		verbose_name_plural = "Uffici - Diritti Generali Delibere"		


class Template_GebevDiritto(Template_Diritto, Entita_GebevDiritto):

	class Meta:
		verbose_name = "Template - Diritto Generale Delibere"	
		verbose_name_plural = "Templates - Diritti Generali Delibere"


# GebevRipartizione

class Entita_GebevRipartizione(Base_abstract):
	diritto = models.ForeignKey(GebevRipartizione, on_delete=models.CASCADE, verbose_name = "Diritto di Gruppo Programma delibere",limit_choices_to={'attivo' : True})
	default = models.BooleanField("Ripartizione di default", default=False, )
	del_v = models.BooleanField("Visibilità delibere", default=True, )
	det_v = models.BooleanField("Visibilità determinazioni", default=True, )
	int_v = models.BooleanField("Visibilità decisioni interne", default=True, )
	dis_v = models.BooleanField("Visibilità disposizioni", default=True, )
	pri_v = models.BooleanField("Visibilità privacy", default=True, )
	del_pt = models.BooleanField("Parere tecnico delibere", default=False, )
	del_pc = models.BooleanField("Parere contabile delibere", default=False, )
	det_pt = models.BooleanField("Parere tecnico determinazioni", default=False, )
	det_pc = models.BooleanField("Parere contabile determinazioni", default=False, )
	int_p = models.BooleanField("Parere decisioni interne", default=False, )

	def sigla(self):
		t_dir=""
		if self.default:
			t_dir += "(default)"
		if self.del_v:
			t_dir +="(DeV)"
		if self.det_v:
			t_dir += "(DtV)"
		if self.int_v:
			t_dir +="(InV)"
		if self.dis_v:
			t_dir += "(DsV)"
		if self.pri_v:
			t_dir += "(PrV)"
		if self.del_pt:
			t_dir +="(DeT)"
		if self.del_pc:
			t_dir += "(DeC)"
		if self.det_pt:
			t_dir +="(DtT)"
		if self.det_pc:
			t_dir += "(DtC)"
		if self.int_p:
			t_dir += "(InP)"
		return t_dir
	
	class Meta:
		abstract = True
		ordering = ["diritto"]


class Atto_GebevRipartizione(Atto_Diritto, Entita_GebevRipartizione):

	def __str__(self):
		text = "{dip} - {diritto}: {diritti}"
		return text.format(dip=self.atto.dipendente, diritto=self.diritto, diritti=self.sigla())
	
	class Meta:
		verbose_name = "Dipendente - Ripartizione Delibere"	
		verbose_name_plural = "Dipendenti - Ripartizioni Delibere"


class Autorizzazione_GebevRipartizione(Autorizzazione_Diritto, Entita_GebevRipartizione):

	def __str__(self):
		text = "{uff} - {diritto}: {diritti}"
		return text.format(uff=self.autorizzazione.ufficio, diritto=self.diritto, diritti=self.sigla())

	class Meta:
		verbose_name = "Ufficio - Ripartizione Delibere"	
		verbose_name_plural = "Uffici - Ripartizioni Delibere"


class Template_GebevRipartizione(Template_Diritto, Entita_GebevRipartizione):

	def __str__(self):
		text = "{tpl} - {diritto}: {diritti}"
		return text.format(tpl=self.template.nome, diritto=self.diritto, diritti=self.sigla())
	
	class Meta:
		verbose_name = "Template - Ripartizione Delibere"	
		verbose_name_plural = "Templates - Ripartizioni Delibere"


# Web
		
class Entita_Web(Base_abstract):
	diritto = models.ForeignKey(Web, on_delete=models.CASCADE, verbose_name = "Diritto Pagine Web",limit_choices_to={'attivo' : True})
	tipo = models.ForeignKey(TipoGenerico, on_delete=models.CASCADE, verbose_name = "Tipologia di diritto", limit_choices_to={'gruppo' : GRUPPO_WEB})
	utente = models.CharField("Utente utilizzato", max_length=70, null=True, blank=True, )

	class Meta:
		abstract = True
		ordering = ["diritto"]


class Atto_Web(Atto_Diritto, Entita_Web):

	class Meta:
		verbose_name = "Dipendente - Diritto Gestione Pagine Web"	
		verbose_name_plural = "Dipendenti - Diritti Gestione Pagine Web"


class Autorizzazione_Web(Autorizzazione_Diritto, Entita_Web):

	class Meta:
		verbose_name = "Ufficio - Diritto Gestione Pagine Web"	
		verbose_name_plural = "Uffici - Diritti Gestione Pagine Web"
  
  
class Template_Web(Template_Diritto, Entita_Web):

	class Meta:
		verbose_name = "Template - Diritto Gestione Pagine Web"	
		verbose_name_plural = "Templates - Diritti Gestione Pagine Web"
  
  

# GOffice2
		
class Entita_GOffice2(Base_abstract):
	diritto = models.ForeignKey(GOffice2, on_delete=models.CASCADE, verbose_name = "App GOffice2",limit_choices_to={'attivo' : True})
	tipo = models.ManyToManyField(TipoGenerico, verbose_name = "Tipologia di diritto", limit_choices_to={'gruppo' : GRUPPO_GOFFICE2})
	# utente = models.CharField("Utente utilizzato", max_length=70, null=True, blank=True, )

	class Meta:
		abstract = True
		ordering = ["diritto"]


class Atto_GOffice2(Atto_Diritto, Entita_GOffice2):

	class Meta:
		verbose_name = "Dipendente - Modulo GOffice2"	
		verbose_name_plural = "Dipendenti - Moduli GOffice2"


class Autorizzazione_GOffice2(Autorizzazione_Diritto, Entita_GOffice2):

	class Meta:
		verbose_name = "Ufficio - Modulo GOffice2"	
		verbose_name_plural = "Uffici - Apps GOffice2"
  
  
class Template_GOffice2(Template_Diritto, Entita_GOffice2):

	class Meta:
		verbose_name = "Template - Modulo GOffice2"	
		verbose_name_plural = "Templates - Moduli GOffice2"