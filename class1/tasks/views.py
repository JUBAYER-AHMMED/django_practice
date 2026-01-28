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

def is_manager(user):
    return user.groups.filter(Q(name="Manager")|Q(name="Admin")).exists()


def is_employee(user):
    return user.groups.filter(Q(name="User")|Q(name="Admin")).exists()


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


@method_decorator(user_passes_test(is_employee, login_url="no_permission"), name="dispatch")
class EmployeeDashboard(View):
    def get(self,request, *args, **kwargs):
        return render(request, "dashboard/user_dashboard.html")

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
    prefetch_related_tasks = Task.objects.prefetch_related('assigned_to').all()
    prefetch_related_emp = User.objects.prefetch_related('tasks').all()
    
    #aggregate
    task_count = Task.objects.aggregate(num_task = Count('id'))
    task_annotate_in_projects = Project.objects.annotate(num_task = Count('task')).order_by('num_task')

    return render(request,
                   "pending.html", 
                    {
                         'prefetch_related_tasks': prefetch_related_tasks,
                         'prefetch_related_emp': prefetch_related_emp,
                         'task_count':task_count,
                         'task_annotate_in_projects':task_annotate_in_projects,
                    })

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


