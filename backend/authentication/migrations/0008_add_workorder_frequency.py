from django.db import migrations


def add_workorder_frequency(apps, schema_editor):
    conn = schema_editor.connection
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'work_order' AND COLUMN_NAME = 'frequency'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE `work_order` ADD COLUMN `frequency` varchar(20) NOT NULL DEFAULT 'One-Time'")


def remove_workorder_frequency(apps, schema_editor):
    conn = schema_editor.connection
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'work_order' AND COLUMN_NAME = 'frequency'")
        if cursor.fetchone()[0] == 1:
            cursor.execute("ALTER TABLE `work_order` DROP COLUMN `frequency`")


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('authentication', '0007_add_workorder_is_active'),
    ]

    operations = [
        migrations.RunPython(add_workorder_frequency, reverse_code=remove_workorder_frequency),
    ]
