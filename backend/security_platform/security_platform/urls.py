"""security_platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
import xadmin
from django.conf.urls import include
from django.urls import re_path

from security_platform.utils import exception_handel_views


urlpatterns = [

    re_path(r'^api/', include('configurations.urls')),
    re_path(r'^api/', include('devices.urls')),
    re_path(r'^api/', include('events.urls')),
    re_path(r'^api/', include('operations.urls')),
    re_path(r'^api/', include('situations.urls')),
    re_path(r'^api/', include('users.urls')),

    re_path(r'xadmin/?', xadmin.site.urls),

]

handler400 = exception_handel_views.bad_request
handler403 = exception_handel_views.permission_denied
handler404 = exception_handel_views.page_not_found
handler500 = exception_handel_views.server_error
