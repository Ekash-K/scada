import os
import sys
import json
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
resp = c.post('/task-master/', {'action':'add','title':'Archive Test Task','description':'Desc','due_date':'2026-07-01'}, follow=True)
print('Create POST status', resp.status_code)
# find workorder
wo = WorkOrder.objects.filter(task_template__title='Archive Test Task').order_by('-id').first()
print('Created workorder id', wo.id, 'is_active:', wo.is_active)
# archive via PATCH
payload = json.dumps({'action': 'archive', 'id': wo.id})
resp = c.generic('PATCH', '/task-master/', data=payload, content_type='application/json')
print('Archive PATCH status', resp.status_code, resp.content[:200])
# refresh
wo.refresh_from_db()
print('After archive is_active:', wo.is_active)
