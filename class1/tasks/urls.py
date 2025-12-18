from django.urls import path
from tasks.views import manager_dashboard,user_dashboard,test,create_task,view_task, filter_data
urlpatterns = [
    path('manager_dashboard/', manager_dashboard),
    path('user_dashboard/', user_dashboard),
    path('test/', test),
    path('create_task/', create_task),
    path('view_task/', view_task),
    path('pending_tasks/', filter_data)
]