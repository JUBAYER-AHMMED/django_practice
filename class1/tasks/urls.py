from django.urls import path
from tasks.views import manader_dashboard,user_dashboard,test,create_task,view_task
urlpatterns = [
    path('manager_dashboard/', manader_dashboard),
    path('user_dashboard/', user_dashboard),
    path('test/', test),
    path('create_task/', create_task),
    path('view_task/', view_task),

]