from django.urls import path
from tasks.views import manager_dashboard,ViewTask, CreateProject,ProjectList,ManagerDashboardView,EmployeeDashboard,DeleteTask,employee_dashboard,create_task,CreateTask,view_task, filter_data,update_task,delete_task,task_details,dashboard,Greetings,HiHowGreetings, ViewProject, TaskDetails,UpdateTask
urlpatterns = [
    # path('manager_dashboard/', manager_dashboard,name="manager-dashboard"),
    path('manager_dashboard/', ManagerDashboardView.as_view(),name="manager-dashboard"),
    # path('user_dashboard/', employee_dashboard, name= "user-dashboard"),
    path('user_dashboard/', EmployeeDashboard.as_view(), name= "user-dashboard"),
    #path('test/', test),
    # path('create_task/', create_task,name = "create-task"),
    path('create_task/', CreateTask.as_view(),name = "create-task"),
    path('create_project/', CreateProject.as_view(),name = "create-project"),
    # path('view_task/', view_task,name="view-task"),
    path('view_task/', ViewTask.as_view(),name="view-task"),
    # path('view_projects/', ViewProject.as_view(),name="view-projects"),
    path('view_projects/', ProjectList.as_view(),name="view-projects-list"),

    path('pending_tasks/', filter_data),
    # path('update_task/<int:id>/', update_task, name = "update-task"),
    path('update_task/<int:id>/', UpdateTask.as_view(), name = "update-task"),
    # path('delete_task/<int:id>/', delete_task, name = "delete-task"),
    path('delete_task/<int:id>/', DeleteTask.as_view(), name = "delete-task"),
    # path('task/<int:task_id>/details', task_details, name = "task_details"),
    path('task/<int:task_id>/details', TaskDetails.as_view(), name = "task_details"),
    path('dashboard/',dashboard,name="dashboard"),
    # path('greetings/', Greetings.as_view(), name='greetings'),
    # path('greetings/', HiHowGreetings.as_view(), name='greetings'),
    path('greetings/', HiHowGreetings.as_view(greetings = ' Hi, Good day.'), name='greetings'),
]