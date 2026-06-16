from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ScadaUser, ScadaSite, ScadaDevice, ScadaTask, ScadaAlert
from django.db.models import Sum

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
        'pending_tasks': ScadaTask.objects.filter(status='Pending').count(),
        'active_tasks': ScadaTask.objects.filter(status='In Progress').count(),
        'recent_tasks': ScadaTask.objects.select_related('assigned_to', 'site').order_by('-created_at')[:5]
    })
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        messages.success(request, "Profile metadata updated successfully.")
        return redirect('profile')
        
    return render(request, 'profile.html', get_global_context(request))

@login_required(login_url='login')
def user_master_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('id')
        
        if action == 'delete' and user_id:
            ScadaUser.objects.filter(id=user_id).delete()
            messages.error(request, "User database profile dropped.")
        else:
            name = (request.POST.get('name') or "").title()
            email = request.POST.get('email')
            category = request.POST.get('category')
            mobile = request.POST.get('mobile')
            site_id = request.POST.get('site_id')
            site_obj = ScadaSite.objects.get(id=site_id) if site_id else None
            
            if action == 'add':
                ScadaUser.objects.create(name=name, email=email, category=category, mobile=mobile, site=site_obj)
                messages.success(request, "New User linked to the tracking matrix.")
            elif action == 'edit' and user_id:
                u = ScadaUser.objects.get(id=user_id)
                u.name, u.email, u.category, u.mobile, u.site = name, email, category, mobile, site_obj
                u.save()
                messages.info(request, "User data configurations updated.")
                
        return redirect('user_master')
        
    users = ScadaUser.objects.select_related('site').all()
    context = get_global_context(request, {
        'users': users,
        'sites': ScadaSite.objects.all(), # Passed to build user insertion select-box dropdown cleanly
        'total_users': users.count(),
        'super_admins': users.filter(category='Super Admin').count(),
        'assigned_users': users.exclude(site__isnull=True).count()
    })
    return render(request, 'user_master.html', context)

@login_required(login_url='login')
def site_master_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        site_id = request.POST.get('id')
        
        if action == 'delete' and site_id:
            ScadaSite.objects.filter(id=site_id).delete()
            messages.error(request, "Site dropped permanently.")
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
        
    sites = ScadaSite.objects.all()
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
            ScadaDevice.objects.filter(id=device_id).delete()
            messages.error(request, "Device hardware reference dropped.")
        else:
            site_obj = ScadaSite.objects.get(id=request.POST.get('site_id'))
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

    devices = ScadaDevice.objects.select_related('site').all()
    context = get_global_context(request, {
        'devices': devices,
        'sites': ScadaSite.objects.all(),
        'total_devices': devices.count(),
        'active_devices': devices.filter(status__iexact='Active').count(),
        'offline_devices': devices.filter(status__iexact='Offline').count()
    })
    return render(request, 'device_master.html', context)

@login_required(login_url='login')
def task_master_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        task_id = request.POST.get('id')
        
        if action == 'delete' and task_id:
            ScadaTask.objects.filter(id=task_id).delete()
            messages.error(request, "Task registration revoked.")
        else:
            user_id = request.POST.get('assigned_to_id')
            site_id = request.POST.get('site_id')
            device_id = request.POST.get('device_id')
            
            params = {
                'title': request.POST.get('title'),
                'description': request.POST.get('description'),
                'priority': request.POST.get('priority', 'Medium'),
                'status': request.POST.get('status', 'Pending'),
                'assigned_to': ScadaUser.objects.get(id=user_id) if user_id else None,
                'site': ScadaSite.objects.get(id=site_id) if site_id else None,
                'device': ScadaDevice.objects.get(id=device_id) if device_id else None,
                'due_date': request.POST.get('due_date') or None
            }
            
            if action == 'add':
                ScadaTask.objects.create(**params)
                messages.success(request, "Field engineering order spawned.")
            elif action == 'edit' and task_id:
                ScadaTask.objects.filter(id=task_id).update(**params)
                messages.info(request, "Field engineering parameters adjusted.")
        return redirect('task_master')
        
    context = get_global_context(request, {
        'tasks': ScadaTask.objects.select_related('assigned_to', 'site', 'device').all(),
        'users': ScadaUser.objects.all(),
        'sites': ScadaSite.objects.all(),
        'devices': ScadaDevice.objects.all()
    })
    return render(request, 'task_master.html', context)

@login_required(login_url='login')
def clear_alert_view(request, alert_id):
    ScadaAlert.objects.filter(id=alert_id).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))