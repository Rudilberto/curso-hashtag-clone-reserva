"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from django.conf.urls.static import static # importamos o static para poder usar no urlpatterns  
from django.conf import settings  # usaremos o settings para importar o MEDIA_URL criado lá

# temos que adicionar aqui os links também, mas podemos fazer isso importando o include e 
# passando o parametro parametro - path('', include('pasta_do_app.urls'))
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('loja.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
