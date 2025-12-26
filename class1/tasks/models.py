from django.db import models



# Create your models here.

class Employee(models.Model):
    name = models.CharField( max_length = 100)
    email = models.EmailField(unique = True)
    #tasks
    def __str__(self):
        return self.name

class Project(models.Model):
    name =  models.CharField(max_length=100)
    description = models.TextField(blank=True,null = True)
    start_date = models.DateField()

    def __str__(self):
        return self.name

class Task(models.Model):
    # project = models.ForeignKey(Project,
    #                             on_delete=models.CASCADE ,
    #                             null = True,
    #                             blank= True 
    #                             )
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED','Completed')
    ]
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE ,
                                default=1
                                )
    
    assigned_to = models.ManyToManyField(Employee,related_name='tasks')


    title = models.CharField(max_length=250)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES,default='PENDING')
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #taskdetail
    def __str__(self):
        return self.title

class TaskDetail(models.Model):
    HIGH = 'H'
    MEDIUM = 'M'
    LOW = 'L'
    PRIORITY_OPTIONS = (
        ( HIGH ,'High'),
        ( MEDIUM,'Medium'),
        ( LOW,'Low'),
    )
    # std_id = models.CharField(max_length=200, primary_key=True)
    task = models.OneToOneField(
        Task,
        on_delete  = models.CASCADE,
        related_name="details"
        )
    # assigned_to = models.CharField(max_length=255)
    priority = models.CharField( max_length = 1, choices = PRIORITY_OPTIONS , default=LOW) 
    notes = models.TextField(blank=True, null = True )
    
    def __str__(self):
        return f'Details form task {self.task.title}'
# Object Relational Mapper ( ORM ):

# from tasks.models import Task
# t = Task(title='Low Priority Task',description='xyz',due_date='2025-12-12') : object creation;
# print(t.title)
# t.save()  : database a save

# Task.objects.get(id=2) : select * from task where id = 2
# TaskDetail.objects.create(task = task, assigned_to = "Jubayer",priority = 'H')


# task = onekgula employee ekta task 
# employee = onek gulo task er jonno assign ase



# python manage.py shell      
# >>>
#  from tasks.models import *
#  e1=Employee.objects.get(id=1)
# >>> e1.tasks.all()
#      <QuerySet [<Task: Task object (3)>]>
# >>> e1.tasks.all().first().title
#  output a title name asbe


# python manage.py makemigrations
# python manage.py migrate                         
