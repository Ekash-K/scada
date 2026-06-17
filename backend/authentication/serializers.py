from rest_framework import serializers
from .models import TaskTemplate, WorkOrder


class TaskTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTemplate
        fields = ['id', 'title', 'description', 'required_json_checklist', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class WorkOrderSerializer(serializers.ModelSerializer):
    # Nested read-only fields for related objects
    task_template_title = serializers.CharField(source='task_template.title', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.name', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = WorkOrder
        fields = [
            'id', 'task_template', 'task_template_title', 
            'assigned_to', 'assigned_to_name', 
            'device', 'device_name', 
            'status', 'frequency', 'due_date', 'parts_used', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']