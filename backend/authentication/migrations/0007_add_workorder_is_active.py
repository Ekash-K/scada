from django.db import migrations


def add_is_active_column(apps, schema_editor):
    conn = schema_editor.connection
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'work_order' AND COLUMN_NAME = 'is_active'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE `work_order` ADD COLUMN `is_active` tinyint(1) NOT NULL DEFAULT 1")


def remove_is_active_column(apps, schema_editor):
    conn = schema_editor.connection
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'work_order' AND COLUMN_NAME = 'is_active'")
        if cursor.fetchone()[0] == 1:
            cursor.execute("ALTER TABLE `work_order` DROP COLUMN `is_active`")


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('authentication', '0006_add_is_active_columns'),
    ]

    operations = [
        migrations.RunPython(add_is_active_column, reverse_code=remove_is_active_column),
    ]
