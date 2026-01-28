from django.shortcuts import render, redirect
from django.http import HttpResponse
from tasks.forms import TaskForm,ProjectForm,TaskModelForm, TaskDetailModelForm
from tasks.models import Task, TaskDetail, Project
from datetime import date, timedelta
from django.contrib.auth.models import User

from django.db.models import Q,Count, Max,Min,Avg
from django.contrib import messages

from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from users.views import is_admin

from django.urls import reverse_lazy
#class based views:
from django.views import View
#method decorators:
from django.utils.decorators import method_decorator
#mixins
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.views.generic.base import ContextMixin
from django.views.generic import ListView,DetailView,UpdateView,DeleteView
class Greetings(View):
    greetings = 'Hello Everyone'

    def get(self,request):
        return HttpResponse(self.greetings)

class HiHowGreetings(Greetings):
    greetings = 'Assalamu alaikum Everyone!'
# Create your views here.

def is_manager(user):
    return user.groups.filter(Q(name="Manager")|Q(name="Admin")).exists()


def is_employee(user):
    return user.groups.filter(Q(name="User")|Q(name="Admin")).exists()


@user_passes_test(is_manager, login_url="no_permission")
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
        'details').prefetch_related('assigned_to').order_by('-created_at')
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

@method_decorator(user_passes_test(is_manager, login_url="no_permission"), name="dispatch")
class ManagerDashboardView(ListView):
    model = Task
    template_name = 'dashboard/manager_dashboard.html'
    context_object_name = 'tasks'
    def get_queryset(self):
        type = self.request.GET.get('type', 'all')
        base_query = Task.objects.select_related(
            'details').prefetch_related('assigned_to').order_by('-created_at')
        if type== 'completed':
            tasks = base_query.filter(status = 'COMPLETED')
        elif type== 'in-progress':
            tasks = base_query.filter(status = 'IN_PROGRESS')
        elif type== 'pending':
            tasks = base_query.filter(status = 'PENDING')
        elif type == 'all':
            tasks = base_query.all()
        return tasks
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['counts'] = Task.objects.aggregate(
            all_tasksCount = Count('id'),
            pending_taskCount =  Count('id', filter=Q(status = 'PENDING')),
            completed_taskCount =  Count('id', filter=Q(status = 'COMPLETED')),
            in_progress_taskCount =  Count('id', filter=Q(status = 'IN_PROGRESS'))  
        )
        return context


@user_passes_test(is_employee, login_url='no_permission')
def employee_dashboard(request):
    return render(request, "dashboard/user_dashboard.html")

@method_decorator(user_passes_test(is_employee, login_url="no_permission"), name="dispatch")
class EmployeeDashboard(View):
    def get(self,request, *args, **kwargs):
        return render(request, "dashboard/user_dashboard.html")

# def test(request):
#     context = {
#         "names": ["Abir","Aman","Akash", "John"],
#         "age": 26,
#     }
#     return render(request, 'test.html', context)


@login_required
@permission_required("tasks.add_task", login_url='no_permission')
def create_task(request):
    
    task_form = TaskModelForm()  #for GET
    task_detail_form = TaskDetailModelForm()  #for GET
    if request.method == "POST":
        
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST, request.FILES)
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




# @method_decorator(login_required, name='dispatch')
# @method_decorator(
#     permission_required("tasks.add_task", login_url='no_permission'),
#     name='dispatch'
# )

class CreateTask(LoginRequiredMixin, PermissionRequiredMixin, ContextMixin,View):
    login_url="no_permission"
    permission_required = "tasks.add_task"
    raise_exception= False

    taskFormTemplate = 'task_form.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task_form"] = kwargs.get( 'task_form',TaskModelForm())
        context["task_detail_form"] = kwargs.get( 'task_detail_form',TaskDetailModelForm())
        return context

    def get(self,request, *args, **kwargs):
        # task_form = TaskModelForm()  #for GET
        # task_detail_form = TaskDetailModelForm()  #for GET
        # context = {"task_form":task_form, "task_detail_form":task_detail_form}
        context = self.get_context_data()
        return render(request, self.taskFormTemplate, context)
    def post(self,request,*args, **kwargs):
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST, request.FILES)
        if task_form.is_valid() and task_detail_form.is_valid():
            
            """ For Model Form Data """
            task = task_form.save()
            task_detail = task_detail_form.save(commit = False)
            task_detail.task = task
            task_detail.save()
            messages.success(request, 'Task created successfully!')
            context = self.get_context_data(task_form=task_form,task_detail_form=task_detail_form)
            return render(request, self.taskFormTemplate, context)


@login_required
@permission_required("tasks.view_task", login_url='no_permission')
def view_task(request):
    # retrieve all data 
    tasks = Task.objects.all()
    # retrieve a specific task 
    # task3 = Task.objects.get(id=3)
    task3 = Task.objects.get(pk=1)
    # task3 = 'one'


    # fetch the first task 
    first_task = Task.objects.first()
    return render(request, "show_task.html", {'tasks': tasks, 'task3': task3, 'first_task': first_task})

view_task_decorators = [login_required, permission_required("tasks.view_task", login_url='no_permission')]
@method_decorator(view_task_decorators, name='dispatch')
class ViewTask(ListView):
    model = Task 
    context_object_name = 'tasks'
    template_name = 'show_task.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['first_task'] = Task.objects.first()
        context["task3"] = Task.objects.filter(pk=1).first()


view_project_decorators = [login_required, permission_required("tasks.view_project", login_url='no_permission')]
@method_decorator(view_project_decorators, name='dispatch')
class ViewProject(ListView):
    model = Project
    context_object_name = 'projects'
    template_name = 'show_projects.html'
    def get_queryset(self):
        queryset = Project.objects.annotate(num_task = Count('task')).order_by('num_task')
        return queryset
    

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
    # prefetch_related_emp = Employee.objects.prefetch_related('tasks').all()
    prefetch_related_emp = User.objects.prefetch_related('tasks').all()
    
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

@login_required
@permission_required("tasks.change_task", login_url='no_permission')
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
        # print("I am called to update.")
        task_form = TaskModelForm(request.POST, instance = task)
        task_detail_form = TaskDetailModelForm(request.POST,request.FILES, instance = task_detail )
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


class UpdateTask(UpdateView):
    model = Task
    form_class = TaskModelForm
    template_name = 'task_form.html'
    context_object_name = 'task'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # task = self.get_object()
        context['task_form'] = self.get_form()
        try:
            task_detail = self.object.details
            # print("running!")

        except TaskDetail.DoesNotExist:
            task_detail = None;
            # print("running2!")

        if task_detail:
            # context['task_detail_form'] = TaskDetailModelForm(instance = task_detail)
            context['task_detail_form'] = TaskDetailModelForm(instance = task_detail)
        else:
            context['task_detail_form'] = TaskDetailModelForm()

        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        task_form = TaskModelForm(request.POST, instance = self.object)
        task_detail_form = TaskDetailModelForm(request.POST,request.FILES, instance = getattr(self.object,'details',None) )
        if task_form.is_valid() and task_detail_form.is_valid():
            """ For Model Form Data """
            task = task_form.save()
            task_detail = task_detail_form.save(commit = False)
            task_detail.task = task
            task_detail.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('update-task', self.object.id)
        context = self.get_context_data()
        context['task_form'] = task_form
        context['task_detail_form'] = task_detail_form
        return render(request, self.template_name, context)

    

@login_required
@permission_required("tasks.delete_task", login_url='no_permission')
def delete_task(request, id):
    if request.method == 'POST':
        task = Task.objects.get(id = id)
        task.delete()
        messages.success(request, 'Task deleted successfully!')
    return redirect('manager-dashboard')

class DeleteTask(LoginRequiredMixin, PermissionRequiredMixin,DeleteView):
    model = Task
    pk_url_kwarg = 'id'
    permission_required = "tasks.delete_task"
    login_url = "signin"
    success_url = reverse_lazy("manager-dashboard")
    template_name = "dashboard/manager_dashboard.html"
    def form_valid(self, form):
        messages.success(self.request, "Task deleted successfully!")
        return super().form_valid(form)

@login_required
@permission_required("tasks.view_task", login_url='no_permission')
def task_details(request, task_id):
    task = Task.objects.get(id=task_id)
    status_choices = Task.STATUS_CHOICES

    if request.method == "POST":
        selected_status = request.POST.get('task_status')
        print(selected_status)
        task.status = selected_status
        task.save()
        return redirect('task_details', task.id)



    return render(request, "task_details.html",{'task':task, 'status_choices':status_choices})


view_taskDetails_decorators = [login_required, permission_required("tasks.view_taskDetails", login_url='no_permission')]
@method_decorator(view_taskDetails_decorators, name='dispatch')
class TaskDetails(DetailView):
    model = Task
    template_name = 'task_details.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Task.STATUS_CHOICES
        return context
    def post(self,request, *args,**kwargs):
        task = self.get_object()
        selected_status = request.POST.get('task_status')
        # print(selected_status)
        task.status = selected_status
        task.save()
        return redirect('task_details', task.id)



create_project_decorators = [login_required, permission_required("tasks.add_project", login_url='no_permission')]
@method_decorator(create_project_decorators, name='dispatch')
class CreateProject(View):
    def get(self, request):
        form = ProjectForm()
        return render(request, 'create_project.html', {'form': form})

    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            return redirect('view-projects-list')
        return render(request, 'create_project.html', {'form': form})

view_project_decorators = [login_required, permission_required("tasks.view_project", login_url='no_permission')]
@method_decorator(view_project_decorators, name='dispatch')
class ProjectList(View):
    def get(self, request):
        print("i am called!")
        projects = Project.objects.all()
        return render(request, 'project_list.html', {'projects': projects})




@login_required
def dashboard(request):
    if is_admin(request.user):
        return redirect('admin_dashboard')
    elif is_manager(request.user):
        return redirect('manager-dashboard')
    elif is_employee(request.user):
        return redirect('user-dashboard')
    
    return redirect('no_permission')


