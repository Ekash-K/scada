from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ScadaUser, ScadaSite, ScadaDevice
from django.db.models import Sum


def login_view(request):
    if request.method == 'POST':
        email_input = request.POST.get('email')
        password_input = request.POST.get('password')
        
        print(f"DEBUG | Attempting email login for: '{email_input}'")
        
        try:
            user_record = User.objects.get(email=email_input)
            internal_username = user_record.username
        except User.DoesNotExist:
           internal_username = None

        user = authenticate(request, username=internal_username, password=password_input)
        
        if user is not None:
            login(request, user)
            print("🟢 SUCCESS: User authenticated successfully using Email!")
            return redirect('dashboard') # Assuming dashboard is next!
        else:
            print("🔴 FAILURE: Invalid email or password.")
            messages.error(request, "Invalid email or password.")
            
    return render(request, 'authentication/login.html')

def signup_view(request):
    if request.method == 'POST':
        email_input = request.POST.get('email')
        password_input = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if not email_input or not password_input:
            messages.error(request, "Please fill out all fields.")
            return render(request, 'authentication/signup.html')
        
        if password_input != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'authentication/signup.html')
            
        if User.objects.filter(email=email_input).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, 'authentication/signup.html')
            
        User.objects.create_user(username=email_input, email=email_input, password=password_input)
        print(f"🟢 SUCCESS: New account created for {email_input}!")
        messages.success(request, "Account created! Please log in.")
        return redirect('login') 
        
    return render(request, 'authentication/signup.html')

def logout_view(request):
    logout(request) 
    print("🔒 Session cleared successfully.")
    return render(request, 'authentication/logout.html')

def forgot_password_view(request):
    if request.method == 'POST':
        messages.info(request, "If that email exists, a password reset link has been dispatched.")
    return render(request, 'authentication/forgotpassword.html')

@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'authentication/dashboard.html')

@login_required(login_url='login')
def user_master_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        raw_name = request.POST.get('name')
        clean_name = raw_name.title() if raw_name else ""

        # 1. DELETE USER
        if action == 'delete':
            user_id = request.POST.get('id')
            ScadaUser.objects.filter(id=user_id).delete()
            messages.error(request, "User permanently deleted.") # Using error for red banner
            
        # 2. EDIT USER
        elif action == 'edit':
            user_id = request.POST.get('id')
            u = ScadaUser.objects.get(id=user_id)
            u.name = clean_name
            u.email = request.POST.get('email')
            u.category = request.POST.get('category')
            u.mobile = request.POST.get('mobile')
            u.site_id = request.POST.get('site_id') or None
            u.save()
            messages.info(request, "User data updated successfully.")
            
        # 3. ADD NEW USER
        elif action == 'add':
            ScadaUser.objects.create(
                name=clean_name,
                email=request.POST.get('email'),
                category=request.POST.get('category'),
                mobile=request.POST.get('mobile'),
                site_id=request.POST.get('site_id') or None
            )
            messages.success(request, "New user added to the grid.")
            
        return redirect('user_master')
    
    users = ScadaUser.objects.all()
    
    context = {
        'users': users,
        'total_users': users.count(),
        'super_admins': users.filter(category='Super Admin').count(),
        'assigned_users': users.exclude(site_id__isnull=True).count()
    }
    return render(request, 'authentication/user_master.html', context)


@login_required(login_url='login')
def site_master_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        # 1. DELETE SITE
        if action == 'delete':
            site_id = request.POST.get('id')
            ScadaSite.objects.filter(id=site_id).delete()
            messages.error(request, "Site permanently deleted.") # Using error for red banner
            
        # 2. EDIT SITE
        elif action == 'edit':
            site_id = request.POST.get('id')
            u = ScadaSite.objects.get(id=site_id)
            u.name = request.POST.get('name')
            u.capacity = request.POST.get('capacity')
            u.latitude = request.POST.get('latitude')
            u.longitude = request.POST.get('longitude')
            messages.info(request, "Site data updated successfully.")
            
        # 3. ADD SITE
        elif action == 'add':
            ScadaSite.objects.create(
                name=request.POST.get('name'),
                capacity=request.POST.get('capacity'),
                latitude=request.POST.get('latitude'),
                longitude=request.POST.get('longitude')
            )
            messages.success(request, "New user added to the grid.")
            
        return redirect('site_master')
    
    sites = ScadaSite.objects.all()
    
    context = {
        'sites': sites,
        'total_sites': sites.count(),
        'total_capacity': sites.aggregate(Sum('capacity'))['capacity__sum']
    }
    return render(request, 'authentication/site_master.html', context)
def device_master_view(request):
    if request.method == 'POST':
        # 1. Grab the hidden action and ID from the modal
        action = request.POST.get('action')
        device_id = request.POST.get('id')
        
        # 2. Grab all the form inputs (FIXED VARIABLE NAMES)
        name = request.POST.get('name')
        category = request.POST.get('category')
        site_id = request.POST.get('site_id')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        status = request.POST.get('status') or 'Active'

        # 3. Route the action
        if action == 'add':
            try:
                assigned_site = ScadaSite.objects.get(id=site_id)
                ScadaDevice.objects.create(
                    name=name,
                    category=category,
                    site=assigned_site,
                    latitude=latitude,
                    longitude=longitude,
                    status=status
                )
                messages.success(request, f"Device '{name}' added successfully.")
            except Exception as e:
                print(f"System Error (Add): {e}") 
                messages.error(request, f"Failed to add device: {e}")
                
        elif action == 'edit':
            try:
                device = ScadaDevice.objects.get(id=device_id)
                device.name = name
                device.category = category
                device.site = ScadaSite.objects.get(id=site_id)
                device.latitude = latitude
                device.longitude = longitude
                device.status = status
                device.save()
                messages.success(request, f"Device '{name}' updated.")
            except Exception as e:
                print(f"System Error (Edit): {e}")
                messages.error(request, f"Failed to edit device: {e}")

        elif action == 'delete':
            try:
                if device_id:
                    ScadaDevice.objects.filter(id=device_id).delete()
                    messages.error(request, "Device permanently deleted.")
                else:
                    messages.error(request, "No device was selected for deletion.")
            except Exception as e:
                print(f"System Error (Delete): {e}")
                messages.error(request, f"Failed to delete device: {e}")

        return redirect('device_master')

    devices = ScadaDevice.objects.select_related('site').all()
    sites = ScadaSite.objects.all()

    # Ensure existing blank device statuses do not break the dashboard counts
    ScadaDevice.objects.filter(status='').update(status='Active')

    total_devices = devices.count()
    active_devices = devices.filter(status__iexact='Active').count()
    offline_devices = devices.filter(status__iexact='Offline').count()

    context = {
        'devices': devices,
        'sites': sites,
        'total_devices': total_devices,
        'active_devices': active_devices,
        'offline_devices': offline_devices,
    }
    
    # This render handles the GET request!
    return render(request, 'authentication/device_master.html', context)