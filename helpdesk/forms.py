# -*- coding: utf-8 -*-
from django import forms

class FormAllegato(forms.Form):
	nome = forms.CharField(label="nome dell'allegato", max_length=120)
	file = forms.FileField(label="file da allegare", required=True)
