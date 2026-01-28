from django import forms
import re 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import  Group, Permission
# from django.contrib.auth.models import User
from tasks.forms import StyledFormMixin
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm,PasswordResetForm, SetPasswordForm
from users.models import CustomUser
from django.contrib.auth import get_user_model
User = get_user_model()

class StyledFormMixin2:
    default_classes = (
        "border-2 border-gray-300 p-1 w-full rounded-lg shadow-sm "
        "focus:border-rose-500 focus:ring-rose-500"
    )

    def apply_styled_widgets(self):
        for field_name, field in self.fields.items():
            classes = self.default_classes
      
            if field_name == "username":
                classes += " bg-rose-200"
            
            label = field.label if field.label else field_name.replace('_', ' ')
            field.widget.attrs['placeholder'] = f"Enter {label.lower()}"
            field.widget.attrs["class"] = classes




class StyledFormMixin3:
    """
    Mixin to apply consistent styling to Django form fields.
    Compatible with Form and ModelForm.
    """

    base_classes = (
        "w-full p-3 rounded-lg border border-gray-300 "
        "focus:outline-none focus:ring-2 focus:ring-rose-500 "
        "focus:border-rose-500"
    )

    select_classes = (
        "w-full p-3 rounded-lg border border-gray-300 "
        "bg-white focus:outline-none focus:ring-2 "
        "focus:ring-rose-500 focus:border-rose-500"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            widget = field.widget

            # Select / ModelChoiceField
            if isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", self.select_classes)

            # Text-based inputs
            elif isinstance(
                widget,
                (
                    forms.TextInput,
                    forms.EmailInput,
                    forms.PasswordInput,
                    forms.NumberInput,
                    forms.DateInput,
                ),
            ):
                widget.attrs.setdefault("class", self.base_classes)



class RegisterForm(UserCreationForm):
    class Meta:
       model = User
       fields = ['username','first_name','last_name', 'password1','password2','email']
    
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        
        for fieldname in ['username','password1','password2']:
          self.fields[fieldname].help_text = None


class customRegistraionForm(StyledFormMixin2,forms.ModelForm):
   password1 = forms.CharField(widget=forms.PasswordInput)
   confirm_password = forms.CharField(widget=forms.PasswordInput)
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   # AuthenticationForm init FIRST
        self.apply_styled_widgets() 
   
   class Meta:
      model = User
      fields = ['username','first_name','last_name', 'password1','confirm_password','email']

   def clean_email(self):
      email = self.cleaned_data.get('email')
      email_exists = User.objects.filter(email = email).exists()

      if email_exists:
         raise forms.ValidationError('email already exist!')
      
      return email

   def clean_password1(self):
      password1 = self.cleaned_data.get('password1')
      errors = []

      if len(password1)<8:
         errors.append('Password must be 8 characters long.')

      if not re.search(r'[A-Z]',password1):
         errors.append('Password must include at least one uppercase letter.')
      if not re.search(r'[a-z]',password1):
         errors.append('Password must include at least one lowercase letter.')
      if not re.search(r'[0-9]',password1):
         errors.append('Password must include at least one number.')
      if not re.search(r'[@#$%^&+=]',password1):
         errors.append('Password must include at least one special character.')
         


      # if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]',password1):
      #    errors.append('password can include uppercase,lowercase,number,special characters: @#$%^&+=')
      
      # if 'abc' not in password1:
      #    errors.append("password must include abc")
      if errors:
         raise forms.ValidationError(errors)
      
      return password1
   
   
   
   def clean(self):   #non-field error
      cleaned_data = super().clean()
      password1 = cleaned_data.get('password1')
      confirm_password = cleaned_data.get('confirm_password')

      if password1 != confirm_password:
         raise forms.ValidationError('password did not match!')
      
      return cleaned_data
   



class LoginForm(AuthenticationForm, StyledFormMixin2):
   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)   # AuthenticationForm init FIRST
      self.apply_styled_widgets()         # styling LAST



class AssignRoleForm(StyledFormMixin3,forms.Form):
   role = forms.ModelChoiceField(
      queryset = Group.objects.all(),
      empty_label = "Selet a Role"
   )

class CreateGroupForm(StyledFormMixin3, forms.ModelForm):
   permissions = forms.ModelMultipleChoiceField(
      queryset = Permission.objects.all(),
      widget = forms.CheckboxSelectMultiple,
      required = False,
      label="Assign Permission"
   )
   class Meta:
      model = Group
      fields = ['name', 'permissions']

class CustomPasswordChangeForm(StyledFormMixin2,PasswordChangeForm):
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   # AuthenticationForm init FIRST
        self.apply_styled_widgets()  

class CustomPasswordResetForm(StyledFormMixin2,PasswordResetForm):
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   # AuthenticationForm init FIRST
        self.apply_styled_widgets()
        
class CustomPasswordResetConfirmForm(StyledFormMixin2,SetPasswordForm):
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   # AuthenticationForm init FIRST
        self.apply_styled_widgets()  


"""
class EditProfileForm(StyledFormMixin, forms.ModelForm):
   class Meta:
      model = User
      fields = ['email','first_name', 'last_name']
   bio = forms.CharField(required=False, widget=forms.Textarea, label='bio')
   profile_image = forms.ImageField(required=False , label='Profile Image')

   def __init__(self, *args, **kwargs):
      print(kwargs)
      self.userprofile = kwargs.pop('userprofile', None)
      super().__init__(*args,**kwargs)

      if self.userprofile:
         self.fields['bio'].initial = self.userprofile.bio
         self.fields['profile_image'].initial = self.userprofile.profile_image

   def save(self, commit = True):
      user =super().save(commit = False)
      if self.userprofile:
         self.userprofile.bio = self.cleaned_data.get('bio')
         self.userprofile.profile_image = self.cleaned_data.get('profile_image')
         if commit:
            self.userprofile.save()

      if commit:
         user.save()

      return user

"""
class EditProfileForm(StyledFormMixin, forms.ModelForm):
   class Meta:
      model = CustomUser
      fields = ['email','first_name', 'last_name','bio','profile_image']
    