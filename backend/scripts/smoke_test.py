import os
import sys
import json
from django.test import Client

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from authentication.models import WorkOrder, TaskTemplate, ScadaUser, ScadaSite, ScadaDevice

c = Client()

print('LOGIN...')
resp = c.post('/login/?next=/dashboard/', {'email': 'user@user.com', 'password': 'user'}, follow=True)
print('login status', resp.status_code)
print('dashboard redirect:', resp.redirect_chain[:1])

print('DASHBOARD PAGE...')
resp = c.get('/dashboard/')
print('dashboard status', resp.status_code)
assert resp.status_code == 200, 'Dashboard failed'

print('CREATE TASK...')
resp = c.post('/task-master/', {
    'action': 'add',
    'title': 'Smoke Test Task',
    'description': 'Smoke test description',
    'due_date': '2026-07-01'
}, follow=True)
print('task-master post status', resp.status_code)
assert resp.status_code == 200, 'Task create failed'

template = TaskTemplate.objects.filter(title='Smoke Test Task').order_by('-id').first()
assert template is not None, 'TaskTemplate not created'
workorder = WorkOrder.objects.filter(task_template=template, is_active=True).order_by('-id').first()
assert workorder is not None, 'WorkOrder not created'
print('workorder', workorder.id, workorder.status, workorder.is_active)

print('ASSIGN TASK...')
# choose active user and device
user = ScadaUser.objects.filter(is_active=True).first()
device = ScadaDevice.objects.filter(is_active=True).first()
assert user is not None, 'No active user found'
assert device is not None, 'No active device found'
resp = c.post('/task-assignment/', {
    'action': 'edit',
    'id': str(workorder.id),
    'user_id': str(user.id),
    'device_id': str(device.id),
    'status': 'In Progress'
}, follow=True)
print('task-assignment post status', resp.status_code)
assert resp.status_code == 200, 'Task assignment failed'
workorder.refresh_from_db()
print('assigned to', workorder.assigned_to_id, 'device', workorder.device_id, 'status', workorder.status)

print('ARCHIVE TASK...')
payload = json.dumps({'action': 'archive', 'id': workorder.id})
resp = c.generic('PATCH', '/task-master/', data=payload, content_type='application/json')
print('archive status', resp.status_code, resp.content[:200])
assert resp.status_code == 200, 'Archive failed'
workorder.refresh_from_db()
assert workorder.is_active is False, 'WorkOrder not archived'

print('TASK ASSIGNMENT PAGE...')
resp = c.get('/task-assignment/')
print('assignment status', resp.status_code)
assert resp.status_code == 200, 'Task assignment page failed'

print('ALL SMOKE TESTS PASSED')
