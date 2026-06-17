from django.contrib import admin
from django.urls import path, include
from authentication.views import (login_view, signup_view, logout_view, forgot_password_view, dashboard_view, user_master_view,
site_master_view, device_master_view, task_master_view, task_assignment_view, profile_view, clear_alert_view, WorkOrderViewSet, TaskTemplateViewSet)
from rest_framework.routers import DefaultRouter
from authentication.views import MobileLoginAPI

router = DefaultRouter()
router.register(r'work-orders', WorkOrderViewSet, basename='work-order')
router.register(r'task-templates', TaskTemplateViewSet, basename='task-template')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('profile/', profile_view, name='profile'),
    path('user-master/', user_master_view, name='user_master'),
    path('site-master/', site_master_view, name='site_master'),
    path('device-master/', device_master_view, name='device_master'),
    path('task-master/', task_master_view, name='task_master'),
    path('task-assignment/', task_assignment_view, name='task_assignment'),
    path('alert/clear/<int:alert_id>/', clear_alert_view, name='clear_alert'),
    path('api/mobile-login/', MobileLoginAPI.as_view(), name='mobile_login'),
    
    # API Endpoints
    path('api/', include(router.urls)),
]