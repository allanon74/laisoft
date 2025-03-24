from django.db import models
import datetime


# models CORSI


# classi astratte

class Base_abstract(models.Model):
	id = models.AutoField("Codice Identificativo", primary_key=True, )
	class Meta:
		abstract = True

# Classi

class Organizzatore(Base_abstract):
	nome = models.CharField("Nome dell'organizzatore", max_length=100, )
	

class Corso(Base_abstract):
	descrizione = models.CharField('Descrizione', max_length=200)
	data = models.DateField('Data del corso', default=datetime.datetime.now(), )
	organizzatore = models.ForeignKey(Organizzatore, )

