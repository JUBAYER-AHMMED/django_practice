from django.urls import path
from tasks.views import manader_dashboard,user_dashboard,test
urlpatterns = [
    path('manager_dashboard/', manader_dashboard),
    path('user_dashboard/', user_dashboard),
    path('test/', test),
]