from django.db import models
from django.utils.timezone import now

class ScadaSite(models.Model):
    name = models.CharField(max_length=120)
    capacity = models.IntegerField()
    latitude = models.DecimalField(max_digits=11, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'device'
        managed = False

    def __str__(self):
        return self.name

class ScadaTask(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(db_column='description')
    priority = models.CharField(max_length=20, default='Medium')
    status = models.CharField(max_length=20, default='Pending') 
    assigned_to = models.ForeignKey(ScadaUser, on_delete=models.SET_NULL, null=True, blank=True, db_column='assigned_to_id')
    site = models.ForeignKey(ScadaSite, on_delete=models.CASCADE, null=True, blank=True, db_column='site_id')
    device = models.ForeignKey(ScadaDevice, on_delete=models.SET_NULL, null=True, blank=True, db_column='device_id')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task'
        managed = False

class ScadaAlert(models.Model):
    message = models.CharField(max_length=255)
    severity = models.CharField(max_length=20, default='Info') 
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'alert'
        managed = False