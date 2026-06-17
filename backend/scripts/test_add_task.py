import os
import sys
# Ensure backend folder is on path so Django can import core.settings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings')
import django
django.setup()
from django.test import Client
from authentication.models import WorkOrder, TaskTemplate

c = Client()
# login
c.post('/login/?next=/dashboard/', {'email':'user@user.com','password':'user'}, follow=True)
# create task
resp = c.post('/task-master/', {'action':'add','title':'Test Task X','description':'Desc X','due_date':'2026-07-01'}, follow=True)
print('POST status', resp.status_code)
print('Templates:', list(TaskTemplate.objects.filter(title='Test Task X').values_list('id', flat=True)))
print('WorkOrders:', list(WorkOrder.objects.filter(task_template__title='Test Task X').values_list('id','status')))
