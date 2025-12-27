from django.shortcuts import render,redirect
from django.contrib import messages
from users.forms import RegisterForm,customRegistraionForm
from django.contrib.auth import login,authenticate,logout

# Create your views here.
def signup(request):
    if request.method == 'GET':
        form = customRegistraionForm()
    elif request.method == 'POST':
        form = customRegistraionForm(request.POST)
        if form.is_valid():
            form.save()
            # print('saved')
            messages.success(request, "Account created successfully")
            return redirect('signup')
        else:
            print('Form is invalid!')
    return render(request,'registration/register.html', {"form": form})

def signin(request):
    if request.method == 'POST':
    #    print(request.POST)
    #    print(request.POST.get('username'))
      username = request.POST.get('username')
      password = request.POST.get('password')

      user = authenticate(request,username=username, password = password)
      print(user)
      if user is not None:
          login(request,user)
          return redirect('home')
    return render(request, 'registration/signin.html')

def signout(request):
    if request.method == "POST":
        logout(request)
        return redirect('signin')
