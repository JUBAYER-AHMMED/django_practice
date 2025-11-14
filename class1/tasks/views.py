from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def home(request):
    #work with db
    #transform data
    #data pass
    #http / json response
    # return HttpResponse("Welcome to the task management system")

    return render(request,"home.html")

def contact(request):
    return HttpResponse("<h1 style='color:red'>This is contact page<h1>")

def show_task(request):
    return HttpResponse("This is our task Page.")

def show_specific_task(request,id):
    print("id: " , id)
    print("id type : ", type(id))
    return HttpResponse(f"This is specific task page {id} ")

