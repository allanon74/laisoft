from django.db import models

class VoceTitolario(models.Model):
	id = models.CharField("Codice Classifica", max_length=20, primary_key=True, )
	descrizione = models.CharField("Descrizione della voce di titolario", max_length= 200, )
	order = models.IntegerField("ordinale di presenzazione dell'elenco", null=True, )
	
	def __str__(self):
		return '%s - %s' % (self.id, self.descrizione)

	class Meta:
		verbose_name = "voce di titolario"
		verbose_name_plural = "voci di titolario"

		
class Gruppo(models.Model):
	id = models.CharField("Codice Gruppo", max_length=20, primary_key=True, )
	descrizione = models.CharField("Descrizione del gruppo", max_length= 150, )

	def __str__(self):
		return '%s - %s' % (self.id, self.descrizione)
		
	class Meta:
		verbose_name = "gruppo"
		verbose_name_plural = "gruppi"

class Tipo(models.Model):
	nome = models.CharField(max_length=200)
	# classifica = models.CharField("Classificazione", max_length=100, blank=True, null=True, )
	# titolari = models.CharField("Gruppo Titolare", max_length=50, blank=True, null=True, )
	# visibilità = models.CharField("Gruppo/i in Visibilità", max_length=100, blank=True, null=True,  )
	
	classifica = models.ForeignKey(VoceTitolario, on_delete=models.SET_NULL, verbose_name="Voce di Titolario", blank=True, null=True, )
	titolari = models.ForeignKey(Gruppo, on_delete=models.SET_NULL, verbose_name="Gruppo Titolare", blank=True, null=True, )
	visibilita = models.ManyToManyField(Gruppo, related_name= "tipo_visibilita", verbose_name="Gruppo/i in Visibilità", blank=True, )
	
	nota = models.TextField("Annotazioni", blank=True, null=True, )
	temporaneo = models.BooleanField("Voce non visualizzata in tabella", default=False, )
	
	def __str__(self):
		return '%s' % (self.nome) 
	
	class Meta:
		verbose_name = "tipologia di documento"
		verbose_name_plural = "tipologie di documento"
	
