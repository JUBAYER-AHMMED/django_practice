from django.db import models
# from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

# class Employee(models.Model):
#     name = models.CharField( max_length = 100)
#     email = models.EmailField(unique = True)
#     #tasks
#     def __str__(self):
#         return self.name

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
    
    # assigned_to = models.ManyToManyField(Employee,related_name='tasks')
    assigned_to = models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='tasks')


    title = models.CharField(max_length=250)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES,default='PENDING')
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
        on_delete  = models.DO_NOTHING,
        related_name="details"
        )
    asset = models.ImageField(upload_to="tasks_asset",blank= True, null = True, default="default_img.png")
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


#signals:

# @receiver(post_save,sender=Task)

# def notify_task_creation(sender,instance,created, **kwargs):
#     if created:
#         print('sender', sender)
#         print('instance', instance)
#         print(kwargs)
#         instance.is_completed = True

#         instance.save()


# #signals
# @receiver(pre_save,sender=Task)

# def notify_task_creation(sender,instance, **kwargs):
#     print('sender', sender)
#     print('instance', instance)
#     print(kwargs)
#     instance.is_completed = True


# @receiver(post_delete, sender = Task)
# def delete_associate_details(sender, instance,**kwargs):
#     if instance.details:
#         print(instance)
#         instance.details.delete()
#         print('deleted successfully')

# @receiver(m2m_changed, sender=Task.assigned_to.through)
# def notify_employees_on_task_creation(sender, instance,action, **kwargs):
#     if action == 'post_add':
#         print(instance, instance.assigned_to.all())
#         assigned_emails = [emp.email for emp in instance.assigned_to.all()]
#         print("checking...", assigned_emails)

#         send_mail(
#             "New Task Assigned",
#             f"You have been assigned to the task: {instance.title}",
#             "jubayerahmmed105@gmail.com",
#             assigned_emails,
#             fail_silently = False
#         )