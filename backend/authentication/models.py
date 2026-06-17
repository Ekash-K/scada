from django.db import models
from django.utils.timezone import now

class ScadaSite(models.Model):
    name = models.CharField(max_length=120)
    capacity = models.IntegerField()
    latitude = models.DecimalField(max_digits=11, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'site'
        managed = False

    def __str__(self):
        return self.name

class ScadaUser(models.Model):
    category = models.CharField(max_length=50) # Roles: Super Admin, SCADA Admin, etc.
    name = models.TextField()
    email = models.CharField(max_length=120, null=True, blank=True)
    mobile = models.CharField(max_length=15)
    password = models.TextField(null=True, blank=True)
    site = models.ForeignKey(ScadaSite, on_delete=models.SET_NULL, null=True, blank=True, db_column='site_id') 
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user'
        managed = False

    def __str__(self):
        return self.name

class ScadaDevice(models.Model):
    name = models.CharField(max_length=120)
    category = models.TextField()
    status = models.CharField(max_length=50)
    site = models.ForeignKey(ScadaSite, on_delete=models.CASCADE, null=True, db_column='site_id') 
    latitude = models.DecimalField(max_digits=11, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    next_inspection = models.DateField(default=now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'device'
        managed = False

    def __str__(self):
        return self.name

class TaskTemplate(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    required_json_checklist = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task_template'

    def __str__(self):
        return self.title

class WorkOrder(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Review Required', 'Review Required'),
        ('Resolved', 'Resolved'),
    ]
    
    task_template = models.ForeignKey(TaskTemplate, on_delete=models.CASCADE, null=True, blank=True, db_column='task_template_id')
    assigned_to = models.ForeignKey(ScadaUser, on_delete=models.SET_NULL, null=True, blank=True, db_column='assigned_to_id')
    device = models.ForeignKey(ScadaDevice, on_delete=models.SET_NULL, null=True, blank=True, db_column='device_id')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    due_date = models.DateField(null=True, blank=True)
    FREQUENCY_CHOICES = [
        ('One-Time', 'One-Time'),
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
    ]
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='One-Time')
    parts_used = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_column='is_active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'work_order'

    def __str__(self):
        return f"WorkOrder - {self.task_template.title if self.task_template else 'Unknown'} ({self.status})"

class ScadaAlert(models.Model):
    message = models.CharField(max_length=255)
    severity = models.CharField(max_length=20, default='Info') 
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'alert'