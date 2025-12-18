from django.shortcuts import render
from django.http import HttpResponse
from tasks.forms import TaskForm,TaskModelForm
from tasks.models import Employee,Task, TaskDetail, Project
from datetime import date, timedelta

from django.db.models import Q,Count, Max,Min,Avg
# Create your views here.
def manager_dashboard(request):
    return render(request, "dashboard/manager_dashboard.html")

def user_dashboard(request):
    return render(request, "dashboard/user_dashboard.html")

def test(request):
    context = {
        "names": ["Abir","Aman","Akash", "John"],
        "age": 26,
    }
    return render(request, 'test.html', context)

def create_task(request):
    # employees = Employee.objects.all()
    #form = TaskForm(employees=employees)  #for GET
    form = TaskModelForm()  #for GET
    if request.method == "POST":
        # form = TaskForm(request.POST, employees = employees)
        form = TaskModelForm(request.POST)
        # print(form)
        if form.is_valid():
            
            """ For Model Form Data """
            form.save()
            return render(request, "task_form.html", {"form": form, 'message':"Task added successfully!"})

            ''' For  Django Form Data'''
            # print(form.cleaned_data)
            # data = form.cleaned_data
            # title = data.get('title')
            # description = data.get('description')
            # due_date = data.get('due_date')
            # assigned_to = data.get('assigned_to')
            # print(title)

            # task = Task.objects.create(title = title,description= description,due_date = due_date )
            # # Assign employee to tasks
            # for emp_id in assigned_to:
            #     employee = Employee.objects.get(id = emp_id)
            #     task.assigned_to.add(employee)

            # return HttpResponse("<h1>Task added successfully!</h1>")
    context = {"form":form}
    return render(request, "task_form.html", context)


def view_task(request):
    # retrieve all data 
    tasks = Task.objects.all()
    # retrieve a specific task 
    # task3 = Task.objects.get(id=3)
    task3 = Task.objects.get(pk=3)

    # fetch the first task 
    first_task = Task.objects.first()
    return render(request, "show_task.html", {'tasks': tasks, 'task3': task3, 'first_task': first_task})

def filter_data(request):
    # pending_tasks = Task.objects.filter(status = "PENDING")
    # today_tasks = Task.objects.filter(due_date = date.today())
    # yesterday = date.today() - timedelta(days=1)
    # yesterday_tasks = Task.objects.filter(due_date=yesterday)

    # # show the tasks whose priority is not low
    # taskDetail = TaskDetail.objects.all()
    # prior_tasks = TaskDetail.objects.exclude(priority = 'L')

    # """Show the task that contain word 'c' and status Pending. """
    # # task_contain = Task.objects.filter(title__icontains = "c" , status ="PENDING")

    # #show the task which are pending or in-progress


    # task_contain = Task.objects.filter(Q(status = "IN_PROGRESS") | Q(status ="PENDING"))

    # isExist = Task.objects.filter(status = 'abc').exists()

    # #select related (Foreign key,, OneToOne field)
    # all_tasks = Task.objects.all() #too may queries happeed
    # selected_tasks= Task.objects.select_related('details').all()
    # selected_tasks= TaskDetail.objects.select_related('task').all()
    

    #for foreign key:
    # selected_tasks= Task.objects.select_related('project').all()

    '''prefetch related: reverse foreign key, many to many'''
    # prefetch_related_projects = Project.objects.prefetch_related('task_set').all()
    
    
    prefetch_related_tasks = Task.objects.prefetch_related('assigned_to').all()
    prefetch_related_emp = Employee.objects.prefetch_related('tasks').all()
    
    #aggregate
    task_count = Task.objects.aggregate(num_task = Count('id'))
    task_annotate_in_projects = Project.objects.annotate(num_task = Count('task')).order_by('num_task')

    return render(request,
                   "pending.html", 
                  {
                    #   'pending_tasks': pending_tasks, 
                    #   'today_tasks': today_tasks, 
                    #   'yesterday_tasks':yesterday_tasks, 
                    #   'prior_tasks': prior_tasks, 
                    #   'task_contain': task_contain, 
                    #   'isExist': isExist, 
                    #   'all_tasks' : selected_tasks,
                        #  'prefetch_related_projects': prefetch_related_projects,
                         'prefetch_related_tasks': prefetch_related_tasks,
                         'prefetch_related_emp': prefetch_related_emp,
                         'task_count':task_count,
                         'task_annotate_in_projects':task_annotate_in_projects,
                    })


# explore query sets api in documentation: search in google