from django.urls import path
from dipendenti import views
from django.contrib.auth.decorators import login_required
from django.conf.urls.i18n import i18n_patterns

from django.utils.translation import gettext_lazy as _


#_Urls PERSONALE
from . import views

urlpatterns = [
#	path('tabella/', views.tabella_turni, name='tabella_turni'),
#	path('test/', views.tabella_turni_test, name='tabella_turni_test'),
#	path('semplice/', views.tabella_turni_semplice, name='tabella_turni_semplice'),
path('<page_name>/', views.VistaIstruzioni.as_view(), ),
path('', views.VistaIstruzioni.as_view(page_name='istruzioni'), name="istruzioni")
]
