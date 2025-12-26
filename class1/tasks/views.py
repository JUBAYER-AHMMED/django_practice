from django.shortcuts import render, redirect
from django.http import HttpResponse
from tasks.forms import TaskForm,TaskModelForm, TaskDetailModelForm
from tasks.models import Employee,Task, TaskDetail, Project
from datetime import date, timedelta

from django.db.models import Q,Count, Max,Min,Avg
from django.contrib import messages
# Create your views here.
def manager_dashboard(request):
   
    # print(type)
    # all_tasks = Task.objects.select_related(
    #     'details').prefetch_related('assigned_to').all()
    # all_tasksCount = all_tasks.count()
    # # pending_task = Task.objects.filter(status = 'PENDING')
    # # pending_taskCount = pending_task.count()
    # pending_taskCount = Task.objects.filter(status = 'PENDING').count()

    # completed_task = Task.objects.filter(status = 'COMPLETED')
    # completed_taskCount = completed_task.count()
    # in_progress_task = Task.objects.filter(status = 'IN_PROGRESS')
    # in_progress_taskCount = in_progress_task.count()

    type = request.GET.get('type', 'all')
    

    counts = Task.objects.aggregate(
        all_tasksCount = Count('id'),
        pending_taskCount =  Count('id', filter=Q(status = 'PENDING')),
        completed_taskCount =  Count('id', filter=Q(status = 'COMPLETED')),
        in_progress_taskCount =  Count('id', filter=Q(status = 'IN_PROGRESS'))  
        )
    
    #retrieving task data
    base_query = Task.objects.select_related(
        'details').prefetch_related('assigned_to').order_by('created_at')
    if type== 'completed':
        tasks = base_query.filter(status = 'COMPLETED')
    elif type== 'in-progress':
        tasks = base_query.filter(status = 'IN_PROGRESS')
    elif type== 'pending':
        tasks = base_query.filter(status = 'PENDING')
    elif type == 'all':
        tasks = base_query.all()


    context = {
        # 'all_tasks':all_tasks,
        'tasks':tasks,
        # 'all_tasksCount':all_tasksCount,
        # # 'pending_task': pending_task,
        # 'pending_taskCount':pending_taskCount,
        # # 'completed_task':completed_task,
        # 'completed_taskCount':completed_taskCount,
        # # 'in_progress_task':in_progress_task,
        # 'in_progress_taskCount':in_progress_taskCount,
        'counts': counts,
    }

    return render(request, "dashboard/manager_dashboard.html", context)

def user_dashboard(request):
    return render(request, "dashboard/user_dashboard.html")

def test(request):
    context = {
        "names": ["Abir","Aman","Akash", "John"],
        "age": 26,
    }
    return render(request, 'test.html', context)

def create_task(request):
    
    task_form = TaskModelForm()  #for GET
    task_detail_form = TaskDetailModelForm()  #for GET
    if request.method == "POST":
        
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST)
        if task_form.is_valid() and task_detail_form.is_valid():
            
            """ For Model Form Data """
            task = task_form.save()
            task_detail = task_detail_form.save(commit = False)
            task_detail.task = task
            task_detail.save()
            messages.success(request, 'Task created successfully!')
            return redirect('create-task')

            
    context = {"task_form":task_form, "task_detail_form":task_detail_form}
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


def update_task(request, id):
    task = Task.objects.get(id = id)
    task_form = TaskModelForm(instance = task)  #for GET
    try:
      task_detail = task.details
    except TaskDetail.DoesNotExist:
      task_detail = None
    if task_detail:
        task_detail_form = TaskDetailModelForm(instance = task_detail)  #for GET
    else :
        task_detail_form = TaskDetailModelForm()
    if request.method == "POST":
        
        task_form = TaskModelForm(request.POST, instance = task)
        task_detail_form = TaskDetailModelForm(request.POST, instance = task_detail )
        if task_form.is_valid() and task_detail_form.is_valid():
            
            """ For Model Form Data """
            task = task_form.save()
            task_detail = task_detail_form.save(commit = False)
            task_detail.task = task
            task_detail.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('update-task', id)

            
    context = {"task_form":task_form, "task_detail_form":task_detail_form}
    return render(request, "task_form.html", context)


def delete_task(request, id):
    if request.method == 'POST':
        task = Task.objects.get(id = id)
        task.delete()
        messages.success(request, 'Task deleted successfully!')
    return redirect('manager-dashboard')