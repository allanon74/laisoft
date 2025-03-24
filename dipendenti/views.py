from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime
import requests
from django.shortcuts import redirect
from django.conf import settings

from django.urls import reverse_lazy

from dipendenti.models import Dipendente, Logo, Voce, Pagina
# Create your views here.

BASE_URL = settings.BASE_URL

IDLOGO = 1 # logo a colori; per quello grigio, scegliere 2

def wiki(request):
	response = redirect('http://wikilaives/mediawiki/index.php/Pagina_principale')
	return response

def lista(request):
	url = "{base_url}helpdesk/lista/"
	response = redirect(url.format(base_url=BASE_URL))
	return response

class Vista_a(LoginRequiredMixin, TemplateView):
	loggeduser = None
	dipendente = None
	admin = False
	context = {}
	login_url = reverse_lazy('users:login')
	
	def setup(self, request, *args, **kwargs):
		super().setup(request, *args, **kwargs)
		self.context = base_context(request, super().get_context_data())
		self.loggeduser = self.context['loggeduser']
		self.dipendente = self.context['dipendente']
		self.admin = self.context['admin']
	
	class Meta:
		abstract = True


def main_menu(request):
	
	templ = "main.html"
	
# 	loggeduser = request.user
# 	dipendente = None
# 	admin = False
# 	
# 	if "_leifers" in loggeduser.username:
# 		dipendente = Dipendente.objects.get(userid=loggeduser.username)
# 	#admin = loggeduser.groups.filter(name='HelpdeskAdmin').exists()
# 	admin = loggeduser.is_staff
# 	
# 	context = {'Author':'giorgio_leifers'}
# 	context['loggeduser'] = loggeduser
# 	context['dipendente'] = dipendente
# 	context['admin'] = admin
	
	context=base_context(request)
	context['pagine'] = Pagina.online()

	return render(request, templ, context)

def base_context(request, context={'author':'Giorgio Bertoluzza'}):
	loggeduser = request.user
	dipendente = None
	admin = False
	
#	if "_leifers" in loggeduser.username:
#		dipendente = Dipendente.objects.get(userid=loggeduser.username)

	dipendente = Dipendente.get_dipendente(loggeduser)
	
	admin = loggeduser.is_staff
	
	logo = Logo.objects.get(id=1)
	
	webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
	vapid_key = webpush_settings.get('VAPID_PUBLIC_KEY')
	
	sec = ""
	if request.is_secure():
		sec="s"
	
	#context['base_url'] = settings.BASE_URL
	context['author'] = 'Giorgio Bertoluzza'
	context['loggeduser'] = loggeduser
	context['dipendente'] = dipendente
	context['admin'] = admin
	context['logo'] = logo
	context['vapid_key'] = vapid_key
	#context['base_url'] = 'http{secure}://{base}/'.format(base=request.get_host(), secure=sec)
	context['base_url'] = settings.BASE_URL
	context['voce_istruzioni'] = Voce.cerca('istruzioni')
	
	return context

class VistaIstruzioni(Vista_a):
	template_name="istruzioni.html"
	page_name = "-"

	def setup(self, request, *args, **kwargs):
			super().setup(request, *args, **kwargs)
			try:
				self.page_name=kwargs['page_name']
			except:
				pass

	def get_context_data(self, *args, **kwargs):
		self.context['pagina'] = Pagina.cerca(self.page_name)

		return self.context