"""protocollo URL Configuration
   Urls PROTOCOLLO
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog

from django.conf import settings
#from django.conf.urls import re_path
from django.conf.urls.static import static

from dipendenti import views

from django.conf.urls.i18n import i18n_patterns

from django.utils.translation import gettext_lazy as _


# from debug_toolbar.toolbar import debug_toolbar_urls

#import rosetta


urlpatterns = i18n_patterns(
#	path("i18n/", include("django.conf.urls.i18n")),
	path('tabella/', include('tabella.urls')),
	path('turni/', include('turni.urls')),
	path('personale/', include('personale.urls')),
	path('valutazioni/', include('valutazioni.urls')),
	path('pratiche/', include('pratiche.urls')),
	path('helpdesk/', include('helpdesk.urls')),
	path('accessi/', include('accessi.urls')),
	path('gic/', include('gic.urls')),
	path('admin/doc/', include('django.contrib.admindocs.urls')),
	path('admin/', admin.site.urls),
	re_path(r'^rosetta/', include('rosetta.urls')),
	path('accounts/', include('django.contrib.auth.urls')),
	path('', login_required(views.main_menu), name='main'),
    path('istruzioni/', views.VistaIstruzioni.as_view(page_name='istruzioni'), name="istruzioni"),
    path('istruzioni/<page_name>/',  views.VistaIstruzioni.as_view(),),
	path('wiki/', views.wiki, name="wiki"), 
	path(r'^webpush/', include('webpush.urls')),
	path('sw.js', TemplateView.as_view(template_name='sw.js', content_type='application/x-javascript')),
	path("__debug__/", include("debug_toolbar.urls")),
	) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += i18n_patterns(path("admin/", admin.site.urls))
urlpatterns += [path("i18n/", include("django.conf.urls.i18n")),]
urlpatterns += [path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),]
urlpatterns += [path('summernote/', include('django_summernote.urls'))] # summernote 02/12/2024
urlpatterns += [re_path(r'^imagefit/', include('imagefit.urls'))]
# urlpatterns += [path('accounts/', include('django.contrib.auth.urls')),]