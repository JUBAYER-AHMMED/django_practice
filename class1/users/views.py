from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from users.forms import RegisterForm,customRegistraionForm, LoginForm , AssignRoleForm ,CreateGroupForm,CustomPasswordChangeForm, CustomPasswordResetForm, CustomPasswordResetConfirmForm,EditProfileForm
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
# from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch

from django.contrib.auth.views import LoginView,PasswordChangeView, PasswordResetView,PasswordResetConfirmView
from django.views.generic import TemplateView,UpdateView

from django.urls import reverse_lazy
from django.urls import reverse_lazy
#class based views:
from django.views import View
#method decorators:
from django.utils.decorators import method_decorator
#mixins
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.views.generic.base import ContextMixin
from django.views.generic import ListView,DetailView,UpdateView,DeleteView

from django.shortcuts import get_object_or_404
from django.views.generic.edit import FormView
# from users.models import UserProfile
from django.contrib.auth import get_user_model
from django.views.generic import CreateView
User = get_user_model()
# Create your views here.

class EditProfileView(UpdateView):
    model = User
    form_class=EditProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'
    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return redirect('profile')


#Test for user:
def is_admin(user):
    return user.groups.filter(name = 'Admin').exists()


def signup(request):
    if request.method == 'GET':
        form = customRegistraionForm()
    elif request.method == 'POST':
        form = customRegistraionForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # print('user : ', user)
            user.set_password(form.cleaned_data.get('password1'))
            # print(form.cleaned_data)
            user.is_active = False
            user.save()
            # print('saved')
            messages.success(request, "A confirmation mail sent.Please Check your email.")
            return redirect('signin')
        else:
            print('Form is invalid!')
    return render(request,'registration/register.html', {"form": form})


class CustomLoginView(LoginView):
    form_class = LoginForm

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else super().get_success_url()
    
class ChangePassword(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm

    
def activate_user(request,user_id,token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('signin')
        else:
            return HttpResponse('Invalid ID or Token')
    except User.DoesNotExist:
        return HttpResponse('User not found!')


@method_decorator(user_passes_test(is_admin, login_url="no_permission"), name="dispatch")
class AdminDashboard(ListView):
    model = User
    template_name = 'admin/dashboard.html'
    context_object_name = 'users'

    def get_queryset(self):
        queryset = User.objects.prefetch_related(
                Prefetch('groups', queryset= Group.objects.all(), to_attr='all_groups')
            ).all()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for user in context['users']:
            if user.all_groups:
                user.group_name = user.all_groups[0].name
            else:
                user.group_name = 'No Group Assigned'
        return context



@method_decorator(user_passes_test(is_admin, login_url="no_permission"), name="dispatch")
class AssignRoleView(FormView):
    template_name = "admin/assign_role.html"
    form_class = AssignRoleForm
    success_url = reverse_lazy("admin_dashboard")
    pk_url_kwarg = "user_id"

    def dispatch(self, request, *args, **kwargs):
        self.user_obj = get_object_or_404(User, id=kwargs.get(self.pk_url_kwarg))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        role = form.cleaned_data["role"]

        self.user_obj.groups.clear()
        self.user_obj.groups.add(role)

        messages.success(
            self.request,
            f"User {self.user_obj.username} has been assigned to the {role.name} role"
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.user_obj
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        current_group = self.user_obj.groups.first()
        if current_group:
            initial["role"] = current_group
        return initial


@method_decorator(user_passes_test(is_admin, login_url="no_permission"), name="dispatch")
class CreateGroupView(CreateView):
    model = Group
    form_class = CreateGroupForm
    template_name = 'admin/create_group.html'
    success_url = reverse_lazy("create_group")

    def form_valid(self,form):
        response = super().form_valid(form)
        messages.success(self.request, f"Group {self.object.name} has been created.")
        return response



@method_decorator(user_passes_test(is_admin, login_url="no_permission"), name="dispatch")
class GroupListView(ListView):
    model = Group
    template_name = 'admin/group_list.html'
    context_object_name = 'groups'

    def get_queryset(self):
        queryset = Group.objects.prefetch_related('permissions').all()
        return queryset
    
class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name()
        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        # context['bio'] = user.userprofile.bio
        context['bio'] = user.bio
        # context['profile_image'] = user.userprofile.profile_image
        context['profile_image'] = user.profile_image
        return context

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/reset_password.html'
    html_email_template_name = "registration/reset_email.html"

    success_url = reverse_lazy('signin')

    def form_valid(self,form):
        messages.success(self.request, 'A reset email sent.Please Check Your Email.' )
        return super().form_valid(form)
     
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('signin')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        print(context)
        return context


    def form_valid(self,form):
        messages.success(self.request, 'Password has been reset successfully.' )
        return super().form_valid(form)
         