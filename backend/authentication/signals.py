import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from .models import WorkOrder, ScadaDevice

logger = logging.getLogger(__name__)


@receiver(post_save, sender=WorkOrder)
def handle_workorder_resolution(sender, instance, created, update_fields, **kwargs):
    """
    Signal handler for WorkOrder post_save events.
    
    When a WorkOrder status is changed to 'Resolved', this signal:
    1. Retrieves the parts_used value
    2. Finds the associated device's site inventory
    3. Deducts parts_used from LocalInventory stock
    
    Error handling includes validation for:
    - Invalid parts_used conversion
    - Missing LocalInventory record
    - Insufficient inventory stock
    - Database transaction failures
    """
    
    try:
        # Only process updates, not creation
        if created:
            return
        
        # Check if update_fields is provided and contains 'status' (for optimization)
        if update_fields and 'status' not in update_fields:
            return
        
        # Only trigger when status is changed to 'Resolved'
        if instance.status != 'Resolved':
            return
        
        # Validate and convert parts_used to integer
        if not instance.parts_used:
            logger.warning(f"WorkOrder {instance.id}: parts_used is empty, skipping inventory deduction.")
            return
        
        try:
            parts_count = int(instance.parts_used)
        except (ValueError, TypeError) as e:
            logger.error(
                f"WorkOrder {instance.id}: Failed to convert parts_used '{instance.parts_used}' to integer. Error: {str(e)}"
            )
            return
        
        if parts_count <= 0:
            logger.warning(f"WorkOrder {instance.id}: parts_used is {parts_count}, no inventory deduction needed.")
            return
        
        # Get associated device and site
        if not instance.device:
            logger.warning(f"WorkOrder {instance.id}: No device associated, skipping inventory deduction.")
            return
        
        device = instance.device
        site = device.site
        
        if not site:
            logger.warning(f"WorkOrder {instance.id}: Device {device.id} has no associated site, skipping inventory deduction.")
            return
        
        # Attempt to find and update LocalInventory
        try:
            # Import LocalInventory from your models (uncomment when model exists)
            from .models import LocalInventory
            
            inventory = LocalInventory.objects.get(site=site)
            
            # Check if there's sufficient stock
            if inventory.total_stock < parts_count:
                logger.error(
                    f"WorkOrder {instance.id}: Insufficient inventory at site {site.name}. "
                    f"Available: {inventory.total_stock}, Required: {parts_count}"
                )
                # Optional: You may want to raise an exception or flag this in the UI
                return
            
            # Deduct parts from inventory
            inventory.total_stock -= parts_count
            inventory.save(update_fields=['total_stock', 'updated_at'])
            
            logger.info(
                f"WorkOrder {instance.id} RESOLVED: Deducted {parts_count} parts from site {site.name}. "
                f"New stock: {inventory.total_stock}"
            )
        
        except ImportError:
            logger.error("LocalInventory model not found. Ensure the model is defined in your models.py")
        
        except ObjectDoesNotExist:
            logger.error(
                f"WorkOrder {instance.id}: No LocalInventory record found for site {site.name}. "
                f"Consider creating an inventory entry for this site."
            )
        
        except Exception as e:
            logger.error(
                f"WorkOrder {instance.id}: Unexpected error while updating inventory. Error: {str(e)}"
            )
    
    except Exception as e:
        logger.critical(f"Critical error in handle_workorder_resolution signal: {str(e)}")
