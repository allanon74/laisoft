from django.db import models
from django.conf import settings
from dipendenti.models import Dipendente, Dirigente

# Create your models here.

# Variabili 

DIRITTO_D3 = "D3"
TESTO = "TX"
GENERICO = "GE"
GRUPPO_O365 = "GO"
GEBEV = "GB"
ATTO = "AT"
DESIGNAZIONE = "DE"
GRUPPO_WEB ="WW"
GRUPPO_SAMBA = "SA"

gruppi_tipo =[
	(DIRITTO_D3, 'Diritto D3'),
	(TESTO, 'Testo'),
	(GENERICO, 'Generico'),
	(GRUPPO_O365, 'Gruppo Office365'),
	(GEBEV, 'Programa delibere'),
	(ATTO, "Atto"),
	(DESIGNAZIONE, "Designazione"),
	(GRUPPO_WEB, "Gruppo Web"),
	(GRUPPO_SAMBA, "Gruppo Samba")
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
	data = models.DateField("Data dell'atto", )
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
	nome = models.CharField("Nome del diritto in italiano", max_length = 80, )
	nome_de = models.CharField("Nome del diritto in tedesco", max_length = 80, null=True, blank=True,)
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

	class Meta:
		verbose_name = "Diritto GOffice"
		verbose_name_plural = "Diritti GOffice"
		ordering = ["nome"]


class D3Gruppo(Diritto):
	nome = models.CharField("Nome del diritto in italiano", max_length = 70, )
	nome_de = models.CharField("Nome del diritto in tedesco", max_length = 70, null=True, blank=True,)
	atti = models.ManyToManyField(
								"Atto", 
								through = "Atto_D3Gruppo",
								related_name = "d3gruppi",
								verbose_name = "Atto di Assegnazione",
								)

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

	class Meta:
		verbose_name = "Gruppo Nextcloud"
		verbose_name_plural = "Gruppi Nextcloud"
		ordering = ["nome"]
	
	
class Porta(Diritto):
	atti = models.ManyToManyField(
								"Atto", 
								through = "Atto_Porta",
								#on_delete = models.CASCADE, 
								related_name = "porta",
								verbose_name = "Atto di Assegnazione",
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

	class Meta:
		verbose_name = "Diritto Pagina Web"
		verbose_name_plural = "Diritti Pagine Web"
		ordering = ["nome"]
			
# Classi Through
		
class Atto_Diritto(Base_abstract):
	atto = models.ForeignKey(Atto, on_delete=models.CASCADE, verbose_name = "Atti",)
#	diritto = models.ForeignKey(Diritto, on_delete=models.CASCADE, verbose_name = "Diritti",)
	data_inserimento = models.DateTimeField("Data di inserimento", auto_now_add=True, )
	data_modifica = models.DateTimeField("Data ultima modifica", auto_now=True, )
	data_disattivazione = models.DateTimeField("Data di disattivazione", null=True, blank=True,)
	utente_inserimento = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE, verbose_name='utente di attribuzione diritto',)
	utente_modifica = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE, verbose_name='utente di modifica diritto',)
	utente_disattivazione = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE, verbose_name='utente di disattivazione diritto', null=True, blank=True, )
	diritto_attivato = models.BooleanField("Diritto assegnato", default=False, )
	utente_admin = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE, verbose_name='Utente amministratore abilitante', null=True, blank=True,)
		
	def __str__(self):
		text = "{dip} - {diritto}"
		return text.format(dip=self.atto.dipendente, diritto=self.diritto)

	class Meta:
		verbose_name = "Dipendente - Diritto"
		verbose_name_plural = "Dipendenti - Diritti"
		abstract = True
		ordering = ["diritto"]


class Atto_GruppoSamba(Atto_Diritto):
	diritto = models.ForeignKey(GruppoSamba, on_delete=models.CASCADE, verbose_name = "Gruppo Samba")
	
	class Meta:
		verbose_name = "Dipendente - Gruppo Samba"	
		verbose_name_plural = "Dipendenti - Gruppi Samba"
		#order_with_respect_to = "diritto"
		ordering = ["diritto"]

class Atto_SGVCanale(Atto_Diritto):
	diritto = models.ForeignKey(SGVCanale, on_delete=models.CASCADE, verbose_name = "Lista Distribuzione SGV")
	
	class Meta:
		verbose_name = "Dipendente - Lista Distribuzione SGV"	
		verbose_name_plural = "Dipendenti - Liste Distribuzione SGV"
		#order_with_respect_to = "diritto"
		ordering = ["diritto"]
		

		
class Atto_GOffice(Atto_Diritto):
	diritto = models.ForeignKey(GOffice, on_delete=models.CASCADE, verbose_name = "Diritto GOffice")
	
	class Meta:
		verbose_name = "Dipendente - Diritto GOffice"	
		verbose_name_plural = "Dipendenti - Diritti GOffice"
		#order_with_respect_to = "diritto"
		ordering = ["diritto"]


class Atto_D3Gruppo(Atto_Diritto):
	diritto = models.ForeignKey(D3Gruppo, on_delete=models.CASCADE, verbose_name = "Diritto di Gruppo D3")
	lettura = models.BooleanField("Lettura documenti", default=False, )
	scrittura = models.BooleanField("Modifica documenti", default=False, )
	lettura_r = models.BooleanField("Lettura documenti riservati", default=False, )
	scrittura_r = models.BooleanField("Modifica documenti riservati", default=False, )
	posta = models.BooleanField("Accesso casella postale", default=False, )

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
		#order_with_respect_to = "diritto"
		ordering = ["diritto"]
		
		
class Atto_D3Diritto(Atto_Diritto):
	diritto = models.ForeignKey(D3Diritto, on_delete=models.CASCADE, verbose_name = "Diritto D3")

	class Meta:
		verbose_name = "Dipendente - Diritto D3"	
		verbose_name_plural = "Dipendenti - Diritti D3"
		#order_with_respect_to = "diritto"		
		ordering = ["diritto"]
		

class Atto_Generico(Atto_Diritto):
	diritto = models.ForeignKey(Generico, on_delete=models.CASCADE, verbose_name = "Sottosistema Ascot")
	tipo = models.ForeignKey(TipoGenerico, on_delete=models.CASCADE, verbose_name = "Tipologia di diritto", limit_choices_to={'gruppo' : GENERICO})

	def __str__(self):
		text = "{dip} - {diritto}: {tipo}"
		return text.format(dip=self.atto.dipendente, diritto=self.diritto, tipo=self.tipo)
	
	class Meta:
		verbose_name = "Dipendente - Diritto Ascot"	
		verbose_name_plural = "Dipendenti - Diritti Ascot"
		#order_with_respect_to = "diritto"
		ordering = ["diritto"]
		

class Atto_DirittoRete(Atto_Diritto):
	diritto = models.ForeignKey(DirittoRete, on_delete=models.CASCADE, verbose_name = "Diritto di Rete")
	annotazioni = models.CharField("Note aggiuntive", max_length=50, null=True, blank=True, )

	class Meta:
		verbose_name = "Dipendente - Diritto di Rete"	
		verbose_name_plural = "Dipendenti - Diritti di Rete"
		#order_with_respect_to = "diritto"
		ordering = ["diritto"]

class Atto_O365Gruppo(Atto_Diritto):
	diritto = models.ForeignKey(O365Gruppo, on_delete=models.CASCADE, verbose_name = "Gruppo Office 365")

	class Meta:
		verbose_name = "Dipendente - Gruppo Office 365"	
		verbose_name_plural = "Dipendenti - Gruppi Office 365"
		#order_with_respect_to = "diritto"	
		ordering = ["diritto"]

class Atto_NextCloud(Atto_Diritto):
	diritto = models.ForeignKey(NextCloud, on_delete=models.CASCADE, verbose_name = "Gruppo NextCloud")
	tipo = models.ForeignKey(TipoGenerico, on_delete=models.CASCADE, verbose_name = "Tipologia di diritto", limit_choices_to={'gruppo' : GENERICO})

	def __str__(self):
		text = "{dip} - {diritto}: {tipo}"
		return text.format(dip=self.atto.dipendente, diritto=self.diritto, tipo=self.tipo)
	
	class Meta:
		verbose_name = "Dipendente - Gruppo NextCloud"	
		verbose_name_plural = "Dipendenti - Gruppi NextCloud"
		#order_with_respect_to = "diritto"	
		ordering = ["diritto"]
		

class Atto_Porta(Atto_Diritto):
	diritto = models.ForeignKey(Porta, on_delete=models.CASCADE, verbose_name = "Porta")

	class Meta:
		verbose_name = "Dipendente - Porta"	
		verbose_name_plural = "Dipendenti - Porte"
		#order_with_respect_to = "diritto"	
		ordering = ["diritto"]


class Atto_WebApp(Atto_Diritto):
	diritto = models.ForeignKey(WebApp, on_delete=models.CASCADE, verbose_name = "Diritto WebApp Django")

	class Meta:
		verbose_name = "Dipendente - Diritto WebApp Django"	
		verbose_name_plural = "Dipendenti - Diritti WebApp Django"
		#order_with_respect_to = "diritto"	
		ordering = ["diritto"]


class Atto_GebevDiritto(Atto_Diritto):
	diritto = models.ForeignKey(GebevDiritto, on_delete=models.CASCADE, verbose_name = "Diritto Generale Programa delibere")

	class Meta:
		verbose_name = "Dipendente - Diritto Generale Delibere"	
		verbose_name_plural = "Dipendenti - Diritti Generali Delibere"
		#order_with_respect_to = "diritto"	
		ordering = ["diritto"]

class Atto_GebevRipartizione(Atto_Diritto):
	diritto = models.ForeignKey(GebevRipartizione, on_delete=models.CASCADE, verbose_name = "Diritto di Gruppo Programma delibere")
	default = models.BooleanField("Ripartizione di default", default=False, )
	del_v = models.BooleanField("Visibilità delibere", default=False, )
	det_v = models.BooleanField("Visibilità determinazioni", default=False, )
	int_v = models.BooleanField("Visibilità decisioni interne", default=False, )
	dis_v = models.BooleanField("Visibilità disposizioni", default=False, )
	pri_v = models.BooleanField("Visibilità privacy", default=False, )
	del_pt = models.BooleanField("Parere tecnico delibere", default=False, )
	del_pc = models.BooleanField("Parere contabile delibere", default=False, )
	det_pt = models.BooleanField("Parere tecnico determinazioni", default=False, )
	det_pc = models.BooleanField("Parere contabile determinazioni", default=False, )
	int_p = models.BooleanField("Parere decisioni interne", default=False, )

	def __str__(self):
		text = "{dip} - {diritto}: {diritti}"
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
		return text.format(dip=self.atto.dipendente, diritto=self.diritto, diritti=t_dir)
	
	class Meta:
		verbose_name = "Dipendente - Ripartizione Delibere"	
		verbose_name_plural = "Dipendenti - Ripartizioni Delibere"	
		#order_with_respect_to = "diritto"	
		ordering = ["diritto"]
		
class Atto_Web(Atto_Diritto):
	diritto = models.ForeignKey(Web, on_delete=models.CASCADE, verbose_name = "Diritto Pagine Web")
	tipo = models.ForeignKey(TipoGenerico, on_delete=models.CASCADE, verbose_name = "Tipologia di diritto", limit_choices_to={'gruppo' : GRUPPO_WEB})
	utente = models.CharField("Utente utilizzato", max_length=70, null=True, blank=True, )

	class Meta:
		verbose_name = "Dipendente - Diritto Gestione Pagine Web"	
		verbose_name_plural = "Dipendenti - Diritti Gestione Pagine Web"
		#order_with_respect_to = "diritto"	
		ordering = ["diritto"]