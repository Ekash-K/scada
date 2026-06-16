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

class ScadaUser(models.Model):
    category = models.CharField(max_length=50)
    name = models.TextField()
    email = models.CharField(max_length=120, null=True, blank=True)
    mobile = models.CharField(max_length=15) # Fixed: Changed to CharField for phone numbers
    password = models.TextField(null=True, blank=True)
    # Fixed: Proper Foreign Key mapped to raw 'site_id' column
    site = models.ForeignKey(ScadaSite, on_delete=models.SET_NULL, null=True, blank=True, db_column='site_id') 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user'
        managed = False

class ScadaDevice(models.Model):
    name = models.CharField(max_length=120)
    category = models.TextField()
    status = models.CharField(max_length=50)
    # Fixed: This allows device.site.name and select_related('site') to actually work
    site = models.ForeignKey(ScadaSite, on_delete=models.CASCADE, null=True, db_column='site_id') 
    latitude = models.DecimalField(max_digits=11, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    next_inspection = models.DateField(default=now) # Added fallback to prevent DB integrity errors
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'device'
        managed = False