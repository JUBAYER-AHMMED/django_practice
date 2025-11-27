from django.shortcuts import render
from django.http import HttpResponse
from tasks.forms import TaskForm,TaskModelForm
from tasks.models import Employee,Task
# Create your views here.
def manader_dashboard(request):
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