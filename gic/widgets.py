# -*- coding: utf-8 -*-
from django.forms.widgets import DateInput, Select

class CustomDate(DateInput):
	template_name = "widgets/custom_date.html"
	
	def format_value(self, value):
		
	#	str = super().format_value(self, value)
		if value == "" or value is None:
			return None
		else: 
			return "{v:%Y-%m-%d}".format(v = value)
		
class CustomSelect(Select):
	template_name = "widgets/custom_select.html"

	"""	
	class Media:
		css = {
				"all": ["css/select2.min.css"]
			}
		js = ['js/select2.min.css',]
		"""

class FilterSelect(Select):
	template_name = "widgets/custom_select_filter.html"

widgets= {
	'custom_date': CustomDate,
	'custom_select': CustomSelect,
	'filter_select' : FilterSelect,
	}