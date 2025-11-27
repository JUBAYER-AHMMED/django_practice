from django.contrib import admin
from django.urls import path,include
from debug_toolbar.toolbar import debug_toolbar_urls
# from tasks.views import home , contact
urlpatterns = [
    path('admin/', admin.site.urls),
    path('tasks/', include("tasks.urls")),
]+ debug_toolbar_urls()


