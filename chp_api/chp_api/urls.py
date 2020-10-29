"""chp_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from rest_framework.urlpatterns import format_suffix_patterns

from chp_handler import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('query/', views.submit_query.as_view()),
    path('checkQuery/', views.check_query.as_view()),
    path('predicates/', views.get_supported_edge_types.as_view()),
    path('nodes/', views.get_supported_node_types.as_view())
]
