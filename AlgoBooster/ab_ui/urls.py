from django.urls import path
from . import views

app_name = 'ab_ui'
urlpatterns = [
	path('', views.index, name='index'),
	path('algobooster/', views.algobooster, name='algobooster'),
	path('algobooster/submit/', views.submit, name='submit'),
	path('training/', views.training, name='training'),
	path('training/submit/', views.train, name='train'),
	path('about', views.about, name='about'),
	path('imprint', views.imprint, name='imprint'),
	path('disclaimer', views.disclaimer, name='disclaimer'),
]
