from django import forms
from tasks.models import Task

# django Form
class TaskForm(forms.Form):
    title = forms.CharField(max_length=250)
    description = forms.CharField(widget=forms.Textarea, label="Task Description")
    due_date=forms.DateField(widget=forms.SelectDateWidget, label='Due Date')
    assigned_to = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices= [])

    def __init__(self,*args,**kwargs):
        # print(args,kwargs)
        employees = kwargs.pop("employees", [])
        # print(employees)
       
        super().__init__(*args,**kwargs)
        # print(self.fields)
        self.fields['assigned_to'].choices = [(emp.id, emp.name) for emp in employees]


class StyledFormMixin:
    """Mixing to apply style"""
    
    default_classes = "border-2 border-gray-300 p-1 w-full rounded-lg shadow-sm focus:border-rose-500 focus:ring-rose-500"

    def apply_styled_widgets(self):
        for field_name,field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class': f"{self.default_classes} bg-gray-200",
                    'placeholder': f"Enter {field.label.lower()}"
                })
            elif isinstance(field.widget,forms.Textarea):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': f"Enter {field.label.lower()}",
                    'rows':5
                }) 
            elif isinstance(field.widget,forms.SelectDateWidget):
                print("I am called!")
                field.widget.attrs.update({
                    'class': "border-2 border-gray-300 p-1 rounded-lg shadow-sm focus:border-rose-500 focus:ring-rose-500",
                }) 
            elif isinstance(field.widget,forms.CheckboxSelectMultiple):
                field.widget.attrs.update({
                    'class': " p-1 rounded-lg "
                })

# Django Model Form
class TaskModelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Task
        # fields = '__all__'
        fields = ['title', 'description','due_date','assigned_to']
        widgets={
            'due_date': forms.SelectDateWidget,
            'assigned_to': forms.CheckboxSelectMultiple
        }



        # exclude = ['project','is_completed','created_at','updated_at']
        '''manual widget'''
        ''' widgets = {
            'title': forms.TextInput(attrs={
                'class': "border-2 border-gray-300 p-1 w-full rounded-lg shadow-sm focus:border-rose-500 focus:ring-rose-500",
                'placeholder': "Enter the title"
            }),
            'description':forms.Textarea(attrs={
                'class': "border-2 border-gray-300 p-1 w-full rounded-lg shadow-sm focus:border-rose-500 focus:ring-rose-500",
                'placeholder': "Describe the task"
            }),
            'due_date': forms.SelectDateWidget(attrs={
                'class': "border-2 border-gray-300 p-1 rounded-lg shadow-sm focus:border-rose-500 focus:ring-rose-500",
            }),
            'assigned_to': forms.CheckboxSelectMultiple(attrs={
                'class': " p-1 rounded-lg ",
            })
        }
        '''

    '''using mixing widget'''
    def __init__(self,*arg,**kwarg):
        super().__init__(*arg, **kwarg)
        self.apply_styled_widgets()