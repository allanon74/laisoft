# -*- coding: utf-8 -*-
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter 
def formatta(value, parameter):
	return value.format(parameter)

