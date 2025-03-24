from django.urls import path

from . import views

urlpatterns = [
	path('test/', views.test, name='test'),
	path('completo/', views.completo, name='completo'),
	path('suggerimento/', views.suggerimento, name='suggerimento'),
	path('pdf/', views.pdf, name='pdf'),
	path('pdfmanual/', views.pdfManual, name='pdfmanual'),
	path('', views.index, name='index'),

]
