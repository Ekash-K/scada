# Django Core Imports
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

# Django REST Framework (Third-Party) Imports
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local App Imports
from .models import ScadaAlert, ScadaDevice, ScadaSite, ScadaUser, TaskTemplate, WorkOrder
from .serializers import TaskTemplateSerializer, WorkOrderSerializer


class WorkOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WorkOrder model.
    Allows: GET (list, retrieve), PUT/PATCH (update), DELETE
    Filters to only return WorkOrders assigned to active users and devices.
    """
    serializer_class = WorkOrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only return WorkOrders where assigned user and device are active
        return WorkOrder.objects.filter(
            Q(assigned_to__is_active=True) | Q(assigned_to__isnull=True),
            Q(device__is_active=True) | Q(device__isnull=True)
        ).filter(is_active=True).select_related('task_template', 'assigned_to', 'device').order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save()
    
    def perform_update(self, serializer):
        serializer.save()


class TaskTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TaskTemplate model.
    Allows: GET (list, retrieve), POST, PUT/PATCH (update), DELETE
    """
    queryset = TaskTemplate.objects.all()
    serializer_class = TaskTemplateSerializer
    permission_classes = [IsAuthenticated]

# Helper context mixin for global items (Alerts panel & common attributes)
def get_global_context(request, extra_context=None):
    context = {
        'live_alerts': ScadaAlert.objects.filter(is_read=False).order_by('-created_at')[:5],
        'alert_count': ScadaAlert.objects.filter(is_read=False).count(),
        'current_web_user': request.user
    }
    if extra_context:
        context.update(extra_context)
    return context

def login_view(request):
    if request.method == 'POST':
        email_input = request.POST.get('email')
        password_input = request.POST.get('password')
        try:
            user_record = User.objects.get(email=email_input)
            internal_username = user_record.username
        except User.DoesNotExist:
            internal_username = None

        user = authenticate(request, username=internal_username, password=password_input)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        email_input = request.POST.get('email')
        password_input = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password_input != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')
            
        if User.objects.filter(email=email_input).exists():
            messages.error(request, "Account with this email already exists.")
            return render(request, 'signup.html')
            
        User.objects.create_user(username=email_input, email=email_input, password=password_input)
        messages.success(request, "Account created! Please log in.")
        return redirect('login') 
    return render(request, 'signup.html')

def logout_view(request):
    logout(request) 
    return render(request, 'logout.html')

def forgot_password_view(request):
    if request.method == 'POST':
        messages.info(request, "If that email exists, a reset link has been dispatched.")
    return render(request, 'forgotpassword.html')

@login_required(login_url='login')
def dashboard_view(request):
    # Aggregated Insights across all components
    total_capacity = ScadaSite.objects.aggregate(Sum('capacity'))['capacity__sum'] or 0
    total_devices = ScadaDevice.objects.count()
    active_devices = ScadaDevice.objects.filter(status__iexact='Active').count()
    
    context = get_global_context(request, {
        'total_sites': ScadaSite.objects.count(),
        'total_capacity': total_capacity,
        'total_users': ScadaUser.objects.count(),
        'total_devices': total_devices,
        'active_devices': active_devices,
        'offline_devices': ScadaDevice.objects.filter(status__iexact='Offline').count(),
        'pending_tasks': WorkOrder.objects.filter(status='Pending').count(),
        'active_tasks': WorkOrder.objects.filter(status='In Progress').count(),
        'recent_tasks': WorkOrder.objects.select_related('assigned_to', 'device', 'task_template').order_by('-created_at')[:5]
    })
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not current_password or not new_password or not confirm_password:
            messages.error(request, "Please complete all password fields to update your credentials.")
            return redirect('profile')

        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect('profile')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('profile')

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Password updated successfully.")
        return redirect('profile')
        
    return render(request, 'profile.html', get_global_context(request))

@login_required(login_url='login')
def user_master_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('id')
        
        if action == 'delete' and user_id:
            ScadaUser.objects.filter(id=user_id).update(is_active=False)
            messages.error(request, "User archived.")
        else:
            name = (request.POST.get('name') or "").title()
            email = request.POST.get('email')
            category = request.POST.get('category')
            mobile = request.POST.get('mobile')
            site_id = request.POST.get('site_id')
            site_obj = ScadaSite.objects.filter(is_active=True).get(id=site_id) if site_id else None
            
            if action == 'add':
                ScadaUser.objects.create(name=name, email=email, category=category, mobile=mobile, site=site_obj)
                messages.success(request, "New User linked to the tracking matrix.")
            elif action == 'edit' and user_id:
                u = ScadaUser.objects.get(id=user_id)
                u.name, u.email, u.category, u.mobile, u.site = name, email, category, mobile, site_obj
                u.save()
                messages.info(request, "User data configurations updated.")
                
        return redirect('user_master')
        
    users = ScadaUser.objects.select_related('site').filter(is_active=True)
    context = get_global_context(request, {
        'users': users,
        'sites': ScadaSite.objects.filter(is_active=True), # Passed to build user insertion select-box dropdown cleanly
        'total_users': users.count(),
        'super_admins': users.filter(category='Super Admin').count(),
        'scada_admins': users.filter(category='SCADA Admin').count(),
        'site_supervisors': users.filter(category='Site Supervisor').count(),
        'site_engineers': users.filter(category='Site Engineer').count()
    })
    return render(request, 'user_master.html', context)

@login_required(login_url='login')
def site_master_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        site_id = request.POST.get('id')
        
        if action == 'delete' and site_id:
            ScadaSite.objects.filter(id=site_id).update(is_active=False)
            messages.error(request, "Site archived.")
        else:
            params = {
                'name': request.POST.get('name'),
                'capacity': request.POST.get('capacity'),
                'latitude': request.POST.get('latitude'),
                'longitude': request.POST.get('longitude')
            }
            if action == 'add':
                ScadaSite.objects.create(**params)
                messages.success(request, "Operational solar domain established.")
            elif action == 'edit' and site_id:
                ScadaSite.objects.filter(id=site_id).update(**params)
                messages.info(request, "Domain parameters modified.")
        return redirect('site_master')
        
    sites = ScadaSite.objects.filter(is_active=True)
    context = get_global_context(request, {
        'sites': sites,
        'total_sites': sites.count(),
        'total_capacity': sites.aggregate(Sum('capacity'))['capacity__sum'] or 0
    })
    return render(request, 'site_master.html', context)

@login_required(login_url='login')
def device_master_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        device_id = request.POST.get('id')
        
        if action == 'delete' and device_id:
            ScadaDevice.objects.filter(id=device_id).update(is_active=False)
            messages.error(request, "Device archived.")
        else:
            site_obj = ScadaSite.objects.filter(is_active=True).get(id=request.POST.get('site_id'))
            params = {
                'name': request.POST.get('name'),
                'category': request.POST.get('category'),
                'site': site_obj,
                'latitude': request.POST.get('latitude'),
                'longitude': request.POST.get('longitude'),
                'status': request.POST.get('status', 'Active')
            }
            if action == 'add':
                ScadaDevice.objects.create(**params)
                messages.success(request, "Asset registered inside grid layer.")
            elif action == 'edit' and device_id:
                ScadaDevice.objects.filter(id=device_id).update(**params)
                messages.info(request, "Asset telemetry properties localized.")
        return redirect('device_master')

    devices = ScadaDevice.objects.select_related('site').filter(is_active=True)
    context = get_global_context(request, {
        'devices': devices,
        'sites': ScadaSite.objects.filter(is_active=True),
        'total_devices': devices.count(),
        'active_devices': devices.filter(status__iexact='Active').count(),
        'offline_devices': devices.filter(status__iexact='Offline').count()
    })
    return render(request, 'device_master.html', context)

@login_required(login_url='login')
def task_master_view(request):
    # Handle PATCH requests for delete (archiving via hard delete)
    if request.method == 'PATCH':
        import json
        try:
            data = json.loads(request.body)
            action = data.get('action')
            task_id = data.get('id')
            
            if action == 'archive' and task_id:
                # Soft-delete: mark work order inactive
                updated = WorkOrder.objects.filter(id=task_id).update(is_active=False)
                if updated:
                    return JsonResponse({'success': True, 'message': 'Task archived successfully'})
                return JsonResponse({'success': False, 'message': 'Task not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        task_id = request.POST.get('id')
        
        try:
            if action == 'delete' and task_id:
                # Soft-delete via is_active flag
                WorkOrder.objects.filter(id=task_id).update(is_active=False)
                messages.error(request, "Task archived.")
            else:
                if action == 'add':
                    title = (request.POST.get('title') or '').strip()
                    description = (request.POST.get('description') or '').strip()
                    due_date = request.POST.get('due_date') or None
                    frequency = request.POST.get('frequency') or 'One-Time'
                    if title:
                        tt = TaskTemplate.objects.create(title=title, description=description)
                        WorkOrder.objects.create(task_template=tt, status='Pending', due_date=due_date, frequency=frequency)
                        messages.success(request, "Work order created.")
                    else:
                        messages.error(request, "Task title is required.")
                elif action == 'edit' and task_id:
                    title = (request.POST.get('title') or '').strip()
                    description = (request.POST.get('description') or '').strip()
                    due_date = request.POST.get('due_date') or None
                    frequency = request.POST.get('frequency') or 'One-Time'
                    task_order = WorkOrder.objects.filter(id=task_id).first()
                    if task_order and task_order.task_template:
                        task_order.task_template.title = title or task_order.task_template.title
                        task_order.task_template.description = description or task_order.task_template.description
                        task_order.task_template.save()
                        task_order.due_date = due_date
                        task_order.frequency = frequency
                        task_order.save()
                        messages.info(request, "Work order updated.")
                    else:
                        messages.error(request, "Unable to update task template.")
                    
        except Exception as e:
            messages.error(request, f"Database Integrity Error: {str(e)}")
            
        return redirect('task_master')
        
    tasks = WorkOrder.objects.select_related('assigned_to', 'device', 'task_template').filter(is_active=True)
    today = timezone.localdate()
    overdue_by_due_date = tasks.filter(status__in=['Pending', 'In Progress']).filter(due_date__lt=today).count()
    context = get_global_context(request, {
        'tasks': tasks,
        'task_templates': TaskTemplate.objects.all(),
        'users': ScadaUser.objects.filter(is_active=True),
        'sites': ScadaSite.objects.filter(is_active=True),
        'devices': ScadaDevice.objects.filter(is_active=True),
        'total_tasks': tasks.count(),
        'pending_tasks': tasks.filter(status='Pending').count(),
        'resolved_tasks': tasks.filter(status='Resolved').count(),
        'overdue_tasks': overdue_by_due_date
    })
    return render(request, 'task_master.html', context)

@login_required(login_url='login')
def task_assignment_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        task_id = request.POST.get('id')
        
        try:
            if action == 'delete' and task_id:
                WorkOrder.objects.filter(id=task_id).update(is_active=False)
                messages.error(request, "Task archived.")
            else:
                if action == 'edit' and task_id:
                    assigned_to_id = request.POST.get('user_id') or None
                    device_id = request.POST.get('device_id') or None

                    params = {
                        'assigned_to_id': assigned_to_id,
                        'device_id': device_id
                    }

                    # If the work order is being assigned to a user or device,
                    # automatically set its status to 'In Progress'. Do not allow
                    # client-side status changes from the form.
                    if assigned_to_id or device_id:
                        params['status'] = 'In Progress'

                    WorkOrder.objects.filter(id=task_id).update(**params)
                    messages.info(request, "Work order assignment updated.")
                    
        except Exception as e:
            messages.error(request, f"Database Integrity Error: {str(e)}")
            
        return redirect('task_assignment')
        
    all_tasks = WorkOrder.objects.select_related('assigned_to', 'device', 'task_template').filter(is_active=True)
    tasks = all_tasks
    context = get_global_context(request, {
        'tasks': tasks,
        'users': ScadaUser.objects.filter(is_active=True),
        'sites': ScadaSite.objects.filter(is_active=True),
        'devices': ScadaDevice.objects.filter(is_active=True),
        'total_tasks': all_tasks.count(),
        'pending_tasks': all_tasks.filter(status='Pending').count(),
        'resolved_tasks': all_tasks.filter(status='Resolved').count(),
        'overdue_tasks': all_tasks.filter(status__in=['Pending', 'In Progress'], due_date__lt=timezone.localdate()).count()
    })
    return render(request, 'task_assignment.html', context)

@login_required(login_url='login')
def clear_alert_view(request, alert_id):
    ScadaAlert.objects.filter(id=alert_id).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

class MobileLoginAPI(APIView):
    permission_classes = [AllowAny] # Let anyone try to log in

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Authenticate the engineer
        user = authenticate(request, username=email, password=password)
        
        if user is not None and user.is_active:
            # Create or retrieve the mobile token
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'name': user.name, # Or whatever your name field is
                'role': user.role
            })
        else:
            return Response({'error': 'Invalid credentials or inactive account'}, status=400)