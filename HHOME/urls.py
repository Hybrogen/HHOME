"""HHOME URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path

from HHOME import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.index),
    path('lightConfig', views.get_light_config),
    path('setLight', views.set_light),
    path('getPorts', views.get_ports),
    path('getMasters', views.get_masters),
    path('getDHT', views.get_data),
    path('addPort', views.add_port),
    path('addLight', views.add_light),
]
