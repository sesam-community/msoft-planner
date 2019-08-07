from django.urls import path

from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('signin', views.sign_in, name='signin'),
  path('authorized', views.callback, name='authorized'),
  path('signout', views.sign_out, name='signout'),
  path('planner', views.planner, name='planner'),
]